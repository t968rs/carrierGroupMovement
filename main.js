import { createCarrierPointPopupContent, createRouteLinePopupContent, fitMapToLayerBounds } from './src/mapInteractions.js';

mapboxgl.accessToken = 'pk.eyJ1IjoidDk2OHJzIiwiYSI6ImNpamF5cTcxZDAwY2R1bWx4cWJvd3JtYXoifQ.XqJkBCgSJeCCeF_yugpG5A';
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/t968rs/cly4kadyt00c401r19uqr7c8e',
    projection: 'globe', // Display the map as a globe, since satellite-v9 defaults to Mercator
    zoom: 3,
    center: [30, 15]
});

// Add user control
map.addControl(new mapboxgl.NavigationControl());

let loc_popup;

// On Load event
map.on('load', () => {
    console.log('Map loaded');
    map.addSource('locations', {
        type: 'geojson',
        data: 'https://raw.githubusercontent.com/t968rs/carrierGroupMovement/master/data/locations.geojson'
    });
    map.addSource('routes', {
        type: 'geojson',
        data: './data/routes.geojson'
    });
    console.log('Locations loaded')
    const images = [
        {name: 'blue-ac', url: 'mapbox-markers/AC_blue1.png'},
        {name: 'gray-ac', url: 'mapbox-markers/AC_gray1.png'},
        {name: 'green-ac', url: 'mapbox-markers/AC_green1.png'}
    ];
    for (let img of images) {
        map.loadImage(img.url, (error, image) => {
            if (error) throw error;
            map.addImage(img.name, image);
        });
    }
    map.addLayer(
        {
            id: 'invisible-locations',
            type: 'circle',
            source: 'locations',
            paint: {
                'circle-radius': 10, // Set radius to 0 so points are invisible
                'circle-opacity': 0, // Set opacity to 0 to make points invisible
                'circle-stroke-width': 0 // Set stroke width to 0 to remove any stroke
            },
            layout: {
                visibility: 'visible' // Ensure the layer is visible
            }
        });
    map.addLayer({
        id: 'command-group-locations',
        type: 'symbol',
        source: 'locations',
        filter: ["all", ["match", ["get", "tm_domain"], ["Current"], true, false]],
        layout: {
            'icon-image': 'blue-ac', // Use the loaded image as the marker
            'icon-size': 0.2,
            'icon-allow-overlap': true
        }
    });
    console.log('Layer added')
});

// Popups for each layer
map.on('click', async (e) => {
    const features = map.queryRenderedFeatures(e.point);
    if (!features.length) {
        console.log('No features found')
        if (loc_popup) {
            loc_popup.remove(); // Close the popup if no feature is clicked
            loc_popup = null;
        }
        return;
    }

    console.log('Features found')
    // Remove any existing popup to prevent content from appending
    if (loc_popup) {
        loc_popup.remove();
    }

    // Handle the features found
    for (const clickedfeature of features) {
        const coordinates = clickedfeature.geometry.coordinates.slice();
        let hullid = features[0].properties["hull_no"];
        let hull_filter = ["==", ["get", "hull_no"], hullid];
        let locid = features[0].properties["loc_id"];
        let loc_filter = ["==", ["get", "loc_id"], locid];

        // Ensure that if the map is zoomed out such that multiple
        // copies of the feature are visible, the popup appears
        // over the copy being pointed to.
        if (['mercator', 'equirectangular'].includes(map.getProjection().name)) {
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            }
        }

        console.log(clickedfeature.properties);
        console.log("Hull Filter: ", hull_filter);
        console.log(clickedfeature.properties);

        const clickedLayer = clickedfeature.layer.id;
        if (['route-layer'].includes(clickedLayer)) {
            console.log('Route layer clicked');
            const sidepopupContent = await createRouteLinePopupContent(clickedfeature);
            // Update custom popup content and display it
            const routePopup = document.getElementById('top-left-popup');
            routePopup.innerHTML = `<ul>${sidepopupContent}</ul>`;
            routePopup.style.display = 'block';
            fitMapToLayerBounds('route-layer');
            return;
        }

        else if (['command-group-locations'].includes(clickedLayer)){
            // Dynamically create HTML content for the popup
            const mapPopupContent = await createCarrierPointPopupContent(clickedfeature);
            // Create the popup
            new mapboxgl.Popup({
                closeButton: true,
                closeOnClick: true,
                anchor: 'bottom', // Adjust anchor as needed (bottom, top, left, right)
                offset: [0, -15] // Adjust offset as needed to make sure popup is visible
            })
            // Display a popup with attributes/columns from the clicked feature
            loc_popup = new mapboxgl.Popup()
                .setLngLat(coordinates)
                .setHTML(mapPopupContent)
                .addTo(map);
            // Add the past and future layers
            if (map.getLayer('past-layer')) {
                console.log('Past layer exists');
                map.setFilter('past-layer',
                    ["all", ["match", ["get", "tm_domain"], ["Past"], true, false],
                        hull_filter]);
            } else {
                console.log('Past layer does not exist')
                map.addLayer({
                    id: 'past-layer',
                    type: 'symbol',
                    source: 'locations',
                    filter: ["all", ["match", ["get", "tm_domain"], ["Past"], true, false],
                        hull_filter],
                    layout: {
                        'icon-image': 'gray-ac', // Use the loaded image as the marker
                        'icon-size': 0.075,
                        'icon-allow-overlap': true
                    }
                })
            }
        // Future layer
        if (map.getLayer('future-layer')) {
            console.log('Future layer exists');
            map.setFilter('future-layer',
                ["all",
                    ["match", ["get", "tm_domain"], ["Future"], true, false],
                    hull_filter]);
        }
        else {
            console.log('Future layer does not exist')
            // Add future layers
            map.addLayer({
                id: 'future-layer',
                type: 'symbol',
                source: 'locations',
                filter: ["all",
                    ["match", ["get", "tm_domain"], ["Future"], true, false],
                    hull_filter],
                layout: {
                    'icon-image': 'green-ac', // Use the loaded image as the marker
                    'icon-size': 0.075,
                    'icon-allow-overlap': true
                }
            })
        }
        // Route Layer
        if (map.getLayer('route-layer')) {
            console.log('Route layer exists');
            map.setFilter('route-layer', loc_filter);
        }
        else {
            console.log('Route layer does not exist')
            map.addLayer({
                id: 'route-layer',
                type: 'line',
                source: 'routes',
                filter: loc_filter,
                paint: {
                    'line-color': '#028663',
                    'line-width': 2
            }
        })
    }
        }
    }

});

// Change the cursor to a pointer when the mouse is over any feature.
map.on('mousemove', (e) => {
    const features = map.queryRenderedFeatures(e.point);
    map.getCanvas().style.cursor = features.length ? 'pointer' : '';
});