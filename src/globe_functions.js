function spinGlobe(map, spinEnabled, userInteracting, maxSpinZoom, slowSpinZoom, secondsPerRevolution) {
        // If the map is not defined, log an error and return.
        if (!map) {
            console.error("map_input is undefined");
            return;
        }
        const zoom = map.getZoom();
        console.log("Current Zoom: ", zoom)
        if (spinEnabled && !userInteracting && zoom < maxSpinZoom) {
            let distancePerSecond = 360 / secondsPerRevolution;
            if (zoom > slowSpinZoom) {
                // Slow spinning at higher zooms
                const zoomDif =
                    (maxSpinZoom - zoom) / (maxSpinZoom - slowSpinZoom);
                distancePerSecond *= zoomDif;
            }
            const center = map.getCenter();
            center.lng -= distancePerSecond;
            // Smoothly animate the map over one second.
            // When this animation is complete, it calls a 'moveend' event.
            map.easeTo({ center, duration: 1000, easing: (n) => n });
        }
    }

// Function to draw route
function drawRoute(map, pastPoint, currentPoint, futurePoint) {
    const route = {
        type: 'Feature',
        geometry: {
            type: 'LineString',
            coordinates: [pastPoint.geometry.coordinates, currentPoint.geometry.coordinates, futurePoint.geometry.coordinates]
        }
    };

    if (map.getSource('route')) {
        map.getSource('route').setData(route);
    } else {
        map.addSource('route', {
            type: 'geojson',
            data: route
        });

        map.addLayer({
            id: 'route',
            type: 'line',
            source: 'route',
            layout: {
                'line-join': 'round',
                'line-cap': 'round'
            },
            paint: {
                'line-color': '#888',
                'line-width': 8
            }
        });
    }
}

export { drawRoute };