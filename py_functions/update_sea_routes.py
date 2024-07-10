import os
import pandas as pd
import geopandas as gpd
import numpy as np
import json
from shapely.geometry import LineString
# from scgraph.geographs.oak_ridge_maritime import oak_ridge_maritime_geograph as sea_routes
from scgraph.geographs.marnet import marnet_geograph as sea_routes
from datetime import datetime


# Import json as dictionary
def read_json_to_dict(file: str) -> dict:
    with open(file, 'r') as f:
        return json.load(f)


def convert_date_dictionary(date_dict):
    for k, v in date_dict.items():
        if isinstance(v, dict):
            for k1, v1 in v.items():
                if v1 is not None and not isinstance(v1, np.datetime64):
                    date_dict[k][k1] = np.datetime64(v1, "s")
        elif v is not None and isinstance(v, np.datetime64):
            date_dict[k] = np.datetime64(v, "s")
    return date_dict


class UpdateSeaRoutes:
    def __init__(self):
        field_dicts = read_json_to_dict("../data/routes_columns.json")
        self.set_attributes_from_dict(field_dicts)
        self.point_locations = "../data/locations.geojson"
        self.output_folder = os.path.split(self.point_locations)[0]

        self.crs = None
        self.route_gdf = None
        self.c_list = None
        self.filename = None

        for v in vars(self):
            var_value = getattr(self, v)
            if var_value is not None:
                if isinstance(var_value, dict):
                    print(f' {v}: dictionary, length: {len(var_value)}')
                else:
                    print(f' {v}: {getattr(self, v)}')

    def set_attributes_from_dict(self, dicts):
        for k, v in dicts.items():
            setattr(self, k, v)

    @staticmethod
    def get_target_date(gdf: gpd.GeoDataFrame, hull_id: str, tm_domain: str):
        # Filter by hull_id
        filtered_gdf = gdf[gdf['hull_id'] == hull_id]
        print(f'HULL: {hull_id}')
        for i, row in filtered_gdf.iterrows():
            print(f'  Row {i} {row["loc_date"]}, {row["tm_domain"]}, {row["loc_id"]}')
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
    def find_relevant_points(gdf_thishull, target_date, hull_id=None):

        if gdf_thishull.empty:
            print(f'  Empty GeoDataFrame: \n{gdf_thishull}')
            return None, None

        # Sort the filtered GeoDataFrame by date
        gdf_thishull = gdf_thishull.sort_values(by='loc_date')
        # print(f' Sorted GDF: \n{gdf}')

        # Init the point dict
        point_dict = {"Past": None, "Current": None, "Future": None}
        dates = {"Past": {"Start": None, "End": target_date},
                 "Future": {"Start": target_date, "End": None}}

        # Find the target point
        current_points = gdf_thishull[gdf_thishull['tm_domain'] == "Current"]
        if current_points.empty:
            point_dict['Current'] = None
        else:
            point_dict['Current'] = (current_points.iloc[0].geometry.x.astype('float64'),
                                     current_points.iloc[0].geometry.y.astype('float64'))

        # Find the most recent past-dated point
        past_points = gdf_thishull[gdf_thishull['loc_date'] < target_date]
        print(f'\n--{hull_id} Past Points: \n{past_points}')
        if past_points.empty:
            point_dict['Past'] = None
            dates['Past']['Start'] = None
            dates['Past']['End'] = None
        else:
            point_dict['Past'] = (past_points.iloc[-1].geometry.x.astype('float64'),
                                  past_points.iloc[-1].geometry.y.astype('float64'))
            dates['Past']['Start'] = past_points.iloc[-1].loc_date
            dates['Past']['End'] = target_date

        # Find the next future-dated point
        future_points = gdf_thishull[gdf_thishull['loc_date'] > target_date]
        if future_points.empty:
            future_points = gdf_thishull[gdf_thishull['tm_domain'] == "Future"]
            if future_points.empty:
                point_dict['Future'] = None
                dates['Future']['End'] = None
        else:
            point_dict['Future'] = (future_points.iloc[0].geometry.x.astype('float64'),
                                    future_points.iloc[0].geometry.y.astype('float64'))
            dates['Future']['End'] = future_points.iloc[0].loc_date
            dates['Future']['Start'] = target_date

        dates = convert_date_dictionary(dates)

        if point_dict['Past'] is None or point_dict['Future'] is None:
            print(f' -- Some unfound points... {hull_id}')
        else:
            print(f'  -- Found past AND Future Points...{hull_id}')

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
        print(f'   Origin: {origin_point}, \n   Destination: {dest_point}')
        route = sea_routes.get_shortest_path(origin_point, dest_point, "mi")
        print(f'  Route: {route["length"]}')
        return route['coordinate_path'], route['length']

    def create_routes(self):

        # Read the GeoDataFrame
        gdf = gpd.read_file(self.point_locations)
        self.crs = gdf.crs
        self.c_list = [c for c in gdf.columns.to_list()]
        print(f'Columns: {self.c_list}, \nCRS: {self.crs}')

        unique_hull_ids = list(set(gdf['hull_id'].values.tolist()))
        print(f'Unique Hull IDs: {unique_hull_ids}')
        # Initialize an empty GeoDataFrame
        all_lines_gdf = gpd.GeoDataFrame(columns=['geometry', 'tm_domain', 'start_date', 'end_date',
                                                  'hull_id', 'loc_id'],
                                         crs=self.crs)

        for ident in unique_hull_ids:
            # Find the relevant points
            target_date = self.get_target_date(gdf=gdf, hull_id=ident, tm_domain="Current")
            hull_gdf = gdf[gdf['hull_id'] == ident]
            current_gdf = hull_gdf[hull_gdf['tm_domain'] == "Current"]
            c_loc_id = current_gdf['loc_id'].values[0]

            point_lookup, dates_lookup = self.find_relevant_points(hull_gdf, target_date, hull_id=ident)

            # Get the routes
            lines = {"Past": None, "Future": None}
            route_lengths = {"Past": None, "Future": None}
            if point_lookup["Past"] and point_lookup["Current"]:
                past_route, route_lengths["Past"] = self.get_routes(point_lookup["Past"], point_lookup["Current"])
                lines["Past"] = LineString(past_route)
                p_loc_id = gdf[(gdf['hull_id'] == ident) & (gdf['loc_date'] == dates_lookup["Past"]["Start"])]
            if point_lookup["Current"] and point_lookup["Future"]:
                future_route, route_lengths['Future'] = self.get_routes(point_lookup["Current"], point_lookup["Future"])
                lines['Future'] = LineString(future_route)
                f_loc_id = gdf[(gdf['hull_id'] == ident) & (gdf['loc_date'] == dates_lookup["Future"]["End"])]

            # Create the GeoDataFrames
            print(f'\n\n')
            for time_domain, line in lines.items():
                print(f' {ident} {time_domain} Current-Date Loc: {c_loc_id}\n  line: {line}')
                if line is not None:
                    print(f' {ident} {time_domain} line exists...')
                    route_length = route_lengths[time_domain]
                    start_date = dates_lookup[time_domain]['Start']
                    end_date = dates_lookup[time_domain]['End']
                    print(f' Length: {route_length}, \n Start: {start_date}, \n End: {end_date}')
                    lines_gdf = gpd.GeoDataFrame({"tm_domain": [time_domain],
                                                  "hull_id": [ident],
                                                  "geometry": [line],
                                                  "length_miles": [round(route_length, 1)],
                                                  "start_date": [start_date], "end_date": [end_date],
                                                  "loc_id": [c_loc_id]},
                                                 geometry="geometry", crs=self.crs)
                    print(f'Lines GDF: \n{lines_gdf}')
                    print(f'Lines GDF geo: \n{lines_gdf.geometry}')
                    print(f'Lines GDF c: \n{lines_gdf.columns.to_list()}')

                    all_lines_gdf = pd.concat([all_lines_gdf, lines_gdf], ignore_index=True)

        # Save the GeoDataFrames
        all_lines_gdf = all_lines_gdf.astype(self.data_types)
        print(f'All Lines GDF: \n{all_lines_gdf.drop(columns=["geometry"])}')
        all_lines_gdf.to_file(os.path.join(self.output_folder, "routes.geojson"), driver="GeoJSON")
        print(f"Saved routes to {self.output_folder} as routes.json")


UpdateSeaRoutes().create_routes()
