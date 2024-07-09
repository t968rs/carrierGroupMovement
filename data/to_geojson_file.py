import os
import geopandas as gpd
from column_dictionary import field_aliases


class WriteNewGeoJSON:
    def __init__(self):
        self.folder_loc = r"A:\carrier_GROUP_data\02_mapping\carrier_group_mapping.gdb"
        self.server_path = os.path.split(__file__)[0]
        print(f'folder_loc: {self.folder_loc}')
        self.loc_path = r"A:\carrier_GROUP_data\02_mapping\zz_shp_dbf_exports\locations.shp"
        self.crs = None
        self.gdf = None
        self.c_list = None
        self.filename = None
        self._init_gdf_from_fc()

    def _init_gdf_from_fc(self):
        # Read Polygon fc
        base, filename = os.path.split(self.loc_path)
        if "." in filename:
            filename = filename.split(".")[0]
        self.filename = filename
        print(f'Base: {base}, \n Filename: {filename}')

        if ".gdb" in base:
            # print(fiona.listlayers(gdb))
            gdf = gpd.read_file(base, driver='FileGDB', layer=filename)
        else:
            gdf = gpd.read_file(self.loc_path)

        self.crs = gdf.crs
        self.c_list = [c for c in gdf.columns.to_list()]
        print(f'Columns: {self.c_list}, \n CRS: {self.crs}')
        self.gdf = gdf

    def rename_columns(self):
        lookup = field_aliases
        for col in self.c_list:
            if col in field_aliases.keys():
                self.gdf.rename(columns={col: field_aliases[col]}, inplace=True)
            else:
                print(f'Column {col} not in field_aliases')
        self.c_list = [c for c in self.gdf.columns.to_list()]
        print(f'Columns: {self.c_list}')

    def gdf_to_geojson(self):
        self.rename_columns()

        driver = "GeoJSON"
        outpath = os.path.join(self.server_path, f"{self.filename}.geojson")
        self.gdf.to_file(filename=outpath, driver=driver,
                         crs=self.crs, mode="w")
        print(f"Saved {self.loc_path} to {outpath}")


WriteNewGeoJSON().gdf_to_geojson()

