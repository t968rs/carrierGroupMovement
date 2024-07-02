var config = {
	/*"requireArcGISLogin": false, // Does the user need to log in to ArcGIS Online or ArcGIS Server?
	"tokenUrl": 'https://www.arcgis.com/sharing/generateToken', // ArcGIS token generation URL*/

	"title": "Carrier Group Movement Map",
	"start": {
		// "maxZoom": 16,
		"center": [38.203,-99.799],
		"zoom": 3,
		"attributionControl": false,
		"zoomControl": false
	},
	"about": {
		"title": "Carrier Group Movement Map",
		"contents": "<p>This page houses a map that tracks global carrier group movements " +
			"" +
			"<p></p>Uses <a href='https://github.com/bmcbride/bootleaf'>Bootleaf map </a>started by Bryan McBride.</p></p>"
	},
	"controls": {
		"zoom": {
			"position": "topleft"
		},
		"leafletGeocoder": {
			//https://github.com/perliedman/leaflet-control-geocoder
			"collapsed": false,
			"position": "topleft",
			"placeholder": "Search for a location",
			"type": "OpenStreetMap", // OpenStreetMap, Google, ArcGIS
			//"suffix": "Australia", // optional keyword to append to every search
			//"key": "AIzaS....sbW_E", // when using the Google geocoder, include your Google Maps API key (https://developers.google.com/maps/documentation/geocoding/start#get-a-key)
		},
		"TOC": {
			//https://leafletjs.com/reference-1.0.2.html#control-layers-option
			"collapsed": false,
			"uncategorisedLabel": "Layers",
			"position": "topright",
			"toggleAll": true
		},
		"history": {
			"position": "bottomleft"
		},
		"bookmarks": {
			"position": "bottomright",
			"places": [
				{
				"latlng": [
					40.7916, -73.9924
				],
				"zoom": 12,
				"name": "Manhattan",
				"id": "a148fa354ba3",
				"editable": true,
				"removable": true
				}
			]
		}
	},

	"activeTool": "filterWidget", // options are identify/coordinates/queryWidget
	"basemaps": ['esriGray', 'esriDarkGray', 'esriStreets', 'OpenStreetMap', "Aerial"],
	"bing_key": "enter your Bing Maps key",
	"mapboxKey": "sk.eyJ1IjoidDk2OHJzIiwiYSI6ImNseTRqeWN5cjAwZ28yaXB4YW4yYjhpZWQifQ.LbYyhDWT7I2t1WEjUqa5gA",
	// "defaultIcon": {
	// 	"imagePath": "https://leafletjs.com/examples/custom-icons/",
	// 	"iconUrl": "leaf-green.png",
	// 	"shadowUrl": "leaf-shadow.png",
	// 	"iconSize":     [38, 95],
	// 		"shadowSize":   [50, 64],
	// 		"iconAnchor":   [22, 94],
	// 		"shadowAnchor": [4, 62],
	// 		"popupAnchor":  [-3, -76]
	// },
	"tocCategories": [
		{
			"name": "GeoJSON layers",
			"layers": ["Group Locations", "Fleets"]
		},
		{
			"name": "ArcGIS Layers",
			"layers" : []
		},
		{
			"name": "WMS/WFS layers",
			"layers": ["US_population", "countries"],
			"exclusive": false
		}
	],
	"projections": [
		{3857: '+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +k=1 +units=m +nadgrids=@null ' +
				'+wktext +no_defs +type=crs '}
	],
	"highlightStyle": {
		"weight": 2,
		"opacity": 1,
		"color": 'white',
		"dashArray": '3',
		"fillOpacity": 0.5,
		"fillColor": '#E31A1C',
		"stroke": true
	},
	"layers": [
	{
    "id": "group locations",
    "type": "geoJSON",
    "cluster": true,
    "showCoverageOnHover": true,
    "minZoom": 12,
    "url": "data/locations.geojson",
    "style": {
        "stroke": true,
        "fillColor": "#00FFFF",
        "fillOpacity": 0.5,
        "radius": 10,
        "weight": 0.5,
        "opacity": 1,
        "color": '#727272'
		  },
		  "icon": {
		      "iconUrl": "./img/blue_boat.png",
		      "iconSize": [24,28]
		  },
		  "visible": true,
		  // "label": {
		  // 	"name": "NAME",
		  // 	"minZoom": 14
		  // }
		}

	]
}
