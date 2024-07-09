import os
import geopandas as gpd
import json


# Import json as dictionary
def read_json_to_dict(file: str) -> dict:
    with open(file, 'r') as f:
        return json.load(f)


class WriteNewGeoJSON:
    def __init__(self):
        field_dicts = read_json_to_dict("column_dictionary.json")
        self.set_attributes_from_dict(field_dicts)

        self.folder_loc = r"A:\carrier_GROUP_data\02_mapping\carrier_group_mapping.gdb"
        self.server_path = os.path.split(__file__)[0]
        self.loc_path = r"A:\carrier_GROUP_data\02_mapping\zz_shp_dbf_exports\locations.shp"
        self.crs = None
        self.gdf = None
        self.c_list = None
        self.filename = None

        for v in vars(self):
            var_value = getattr(self, v)
            if var_value is not None:
                if isinstance(var_value, dict):
                    print(f' {v}: dictionary, length: {len(var_value)}')
                else:
                    print(f' {v}: {getattr(self, v)}')
        self._init_gdf_from_fc()

    def set_attributes_from_dict(self, dicts):
        for k, v in dicts.items():
            setattr(self, k, v)

    def _init_gdf_from_fc(self):
        # Read Polygon fc
        base, filename = os.path.split(self.loc_path)
        if "." in filename:
            filename = filename.split(".")[0]
        self.filename = filename
        print(f'   Base: {base}, \n   Filename: {filename}')

        if ".gdb" in base:
            # print(fiona.listlayers(gdb))
            gdf = gpd.read_file(base, driver='FileGDB', layer=filename)
        else:
            gdf = gpd.read_file(self.loc_path)

        self.crs = gdf.crs
        gdf = self.add_numbered_primary_key(gdf, 'loc_id')
        self.c_list = [c for c in gdf.columns.to_list()]
        print(f'   Input Columns: {self.c_list}, \n   CRS: {self.crs}')
        self.gdf = gdf.astype(self.data_types)

    def rename_columns(self):

        for col in self.c_list:
            if col in self.field_aliases.keys():
                self.gdf.rename(columns={col: self.field_aliases[col]}, inplace=True)
            else:
                if col not in ['geometry']:
                    self.gdf.drop([col], axis=1, inplace=True)
                    print(f'Column {col} not in field_aliases. Dropped.')
        self.c_list = [c for c in self.gdf.columns.to_list()]
        print(f'Columns: {self.c_list}')

    @staticmethod
    def add_numbered_primary_key(gdf, col_name):
        gdf[col_name] = range(1, len(gdf) + 1)
        return gdf

    def gdf_to_geojson(self):

        for c in self.c_list:
            if c not in list(self.field_aliases.keys()) + ['geometry']:
                self.gdf.drop([c], axis=1, inplace=True)
                print(f'     - Dropped {c}')
            else:
                print(f'    {c}: {self.gdf.dtypes[c]}')
        driver = "GeoJSON"
        outpath = os.path.join(self.server_path, f"{self.filename}.geojson")
        self.gdf.to_file(filename=outpath, driver=driver,
                         crs=self.crs, mode="w")
        print(f"Saved {self.loc_path} to {outpath}")


WriteNewGeoJSON().gdf_to_geojson()
