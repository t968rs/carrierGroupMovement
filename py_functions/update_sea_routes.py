import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
from scgraph.geographs.marnet import marnet_geograph
from datetime import datetime


class UpdateSeaRoutes:
    def __init__(self):
        self.point_locations = "../data/locations.geojson"
        self.output_folder = os.path.split(self.point_locations)[0]

        self.crs = None
        self.route_gdf = None
        self.c_list = None
        self.filename = None

    @staticmethod
    def get_target_date(gdf: gpd.GeoDataFrame, hull_id: str, tm_domain: datetime):
        # Filter by hull_id
        filtered_gdf = gdf[gdf['hull_id'] == hull_id]
        print(f'HULL: {hull_id}')
        for i, row in filtered_gdf.iterrows():
            print(f'  Row {i} {row["loc_date"]}, {row["tm_domain"]}')
        # Further filter by tm_domain
        filtered_gdf = filtered_gdf[filtered_gdf['tm_domain'] == tm_domain]
        print(f'  Columns: {filtered_gdf.columns.to_list()}')

        # Ensure there is only one row that matches the criteria
        if len(filtered_gdf) == 1:
            target_date = filtered_gdf['loc_date'].values[0]
            print(f'  Target Date: {target_date}')
            return target_date
        else:
            print(f' Filtered GDF: \n{filtered_gdf["loc_date"]}')
            return None

    @staticmethod
    def find_relevant_points(gdf, target_date, hull_id=None):

        if gdf.empty:
            print(f'  Empty GeoDataFrame: \n{gdf}')
            return None, None, None

        # Sort the filtered GeoDataFrame by date
        filtered_gdf = gdf.sort_values(by='loc_date')
        print(f' Sorted GDF: \n{filtered_gdf}')

        # Init the point dict
        point_dict = {"Past": None, "Current": None, "Future": None}
        dates = {"Past": {"Start": None, "End": target_date},
                 "Future": {"Start": target_date, "End": None}}

        # Find the target point
        target_points = filtered_gdf[filtered_gdf['loc_date'] == target_date]
        if target_points.empty:
            point_dict['Current'] = None
        else:
            point_dict['Current'] = (target_points.iloc[0].geometry.x.astype('float64'),
                                     target_points.iloc[0].geometry.y.astype('float64'))

        # Find the most recent past-dated point
        past_points = filtered_gdf[filtered_gdf['loc_date'] < target_date]
        if past_points.empty:
            point_dict['Past'] = None
            dates['Past']['Start'] = None
        else:
            point_dict['Past'] = (past_points.iloc[-1].geometry.x.astype('float64'),
                                  past_points.iloc[-1].geometry.y.astype('float64'))
            dates['Past']['Start'] = past_points.iloc[-1].loc_date

        # Find the next future-dated point
        future_points = filtered_gdf[filtered_gdf['loc_date'] > target_date]
        if future_points.empty:
            future_points = filtered_gdf[filtered_gdf['tm_domain'] == "Future"]
            if future_points.empty:
                point_dict['Future'] = None
                dates['Future']['End'] = None
        if not future_points.empty:
            point_dict['Future'] = (future_points.iloc[0].geometry.x.astype('float64'),
                                future_points.iloc[0].geometry.y.astype('float64'))
            dates['Future']['End'] = future_points.iloc[0].loc_date

        if point_dict['Past'] and point_dict['Future'] is None:
            print(f' -- Some unfound points...')
            for td, pt in point_dict.items():
                print(f'  {td} Point: {pt}')
        else:
            print(f'  -- Found past AND FUture Points...')
        for td, pt in point_dict.items():
            print(f'  {td} Point: {pt}')
        return point_dict, dates

    @staticmethod
    def get_routes(start, end):
        """
        Get the shortest path between two points using the Marnet API.
        :param start: list of x,y coordinates for the start point
        :param end: list of x,y coordinates for the end point
        :return: list of x,y coordinates for the shortest path
        """

        # Get the shortest path between two points
        origin_point = {'latitude': start[1], 'longitude': start[0]}
        dest_point = {'latitude': end[1], 'longitude': end[0]}
        route = marnet_geograph.get_shortest_path(origin_point, dest_point, "mi")
        print(f'  Route: {route}')
        return route['coordinate_path'], route['length']

    def create_routes(self):

        # Read the GeoDataFrame
        gdf = gpd.read_file(self.point_locations)
        self.crs = gdf.crs
        self.c_list = [c for c in gdf.columns.to_list()]
        print(f'Columns: {self.c_list}, \n CRS: {self.crs}')

        unique_hull_ids = gdf['hull_id'].unique()
        # Initialize an empty GeoDataFrame
        all_lines_gdf = gpd.GeoDataFrame(columns=['geometry', 'tm_domain', 'start_date', 'end_date',
                                                  'hull_id', 'loc_id'],
                                         crs=self.crs)

        for hull_id in unique_hull_ids:
            # Find the relevant points
            filtered_gdf = gdf[gdf['hull_id'] == hull_id]
            print(f' Filtered GDF1: \n{filtered_gdf}')
            target_date = self.get_target_date(gdf=filtered_gdf, hull_id=hull_id, tm_domain="Current")
            loc_id = filtered_gdf[filtered_gdf['loc_date'] == target_date]['loc_id'].values[0]
            point_lookup, dates_lookup = self.find_relevant_points(filtered_gdf, target_date)
            for td, pt in point_lookup.items():
                print(f'{td} Point: {pt}, \n  Type: {type(pt)}')

            # Get the routes
            lines = {"Past": None, "Future": None}
            route_lengths = {"Past": None, "Future": None}
            if point_lookup["Past"] and point_lookup["Current"]:
                past_route, route_lengths["Past"] = self.get_routes(point_lookup["Past"], point_lookup["Current"])
                lines["Past"] = LineString(past_route)
            if point_lookup["Current"] and point_lookup["Future"]:
                future_route, route_lengths['Future'] = self.get_routes(point_lookup["Current"], point_lookup["Future"])
                lines['Future'] = LineString(future_route)

            # Create the GeoDataFrames
            for time_domain, line in lines.items():
                if line is not None:
                    start_date = dates_lookup[time_domain]['Start']
                    end_date = dates_lookup[time_domain]['End']
                    lines_gdf = gpd.GeoDataFrame({"tm_domain": [time_domain],
                                                  "hull_id": [hull_id],
                                                  "geometry": [line],
                                                  "length_miles": [route_lengths[time_domain]],
                                                  "start_date": start_date, "end_date": end_date,
                                                  "loc_id": loc_id},
                                                 geometry="geometry", crs=self.crs)
                    print(f'Lines GDF: \n{lines_gdf}')
                    print(f'Lines GDF geo: \n{lines_gdf.geometry}')
                    all_lines_gdf = pd.concat([all_lines_gdf, lines_gdf], ignore_index=True)

        # Save the GeoDataFrames
        print(f'All Lines GDF: \n{all_lines_gdf}')
        all_lines_gdf.to_file(os.path.join(self.output_folder, "routes.geojson"), driver="GeoJSON")
        print(f"Saved routes to {self.output_folder} as routes.json")


UpdateSeaRoutes().create_routes()
