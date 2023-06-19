function plot_velocity(timestamps, velocities) {
    const trace = {
        x: timestamps,
        y: velocities,
        mode: 'lines',
        name: 'Velocity'
    };

    const max_val = Math.max(...velocities);
    const line = {
        x: [timestamps[0], timestamps[timestamps.length - 1]],
        y: [max_val * 0.1, max_val * 0.1],
        mode: 'lines',
        name: '10% of Max'
    };

    const layout = {
        title: 'Velocity over Time',
        xaxis: {
            title: 'Time'
        },
        yaxis: {
            title: 'Velocity'
        }
    };

    Plotly.newPlot('velocity', [trace, line], layout);
}

function plot_acceleration(timestamps, accelerations) {
    const trace = {
        x: timestamps,
        y: accelerations,
        mode: 'lines',
        name: 'Acceleration'
    };

    const max_val = Math.max(...accelerations);
    const line = {
        x: [timestamps[0], timestamps[timestamps.length - 1]],
        y: [max_val * 0.1, max_val * 0.1],
        mode: 'lines',
        name: '10% of Max'
    };

    const layout = {
        title: 'Acceleration over Time',
        xaxis: {
            title: 'Time'
        },
        yaxis: {
            title: 'Acceleration'
        }
    };

    Plotly.newPlot('acceleration', [trace, line], layout);
}

Promise.all([fetch('/trials'), fetch('/participants'), fetch('/conditions')])
    .then(function (responses) {
        return Promise.all(responses.map(function (response) {
            return response.json();
        }));
    }).then(function (data) {
        var trials = data[0];
        var participants = data[1];
        var conditions = data[2];

        var trialSelect = document.getElementById('trial-select');
        var participantSelect = document.getElementById('participant-select');
        var conditionSelect = document.getElementById('condition-select');

        trials.forEach(function (trial) {
            var option = document.createElement('option');
            option.text = trial;
            trialSelect.add(option);
        });

        participants.forEach(function (participant) {
            var option = document.createElement('option');
            option.text = participant;
            participantSelect.add(option);
        });

        conditions.forEach(function (condition) {
            var option = document.createElement('option');
            option.text = condition;
            conditionSelect.add(option);
        });

        console.log('Dropdowns populated with trials, participants, and conditions');
    }).catch(function (error) {
        console.error('Error fetching trials, participants, or conditions: ', error);
    });

// Handle "Go" button click
document.getElementById('go-button').addEventListener('click', function () {
    var trial = document.getElementById('trial-select').value;
    var participant = document.getElementById('participant-select').value;
    var condition = document.getElementById('condition-select').value;

    console.log(`Fetching data for trial "${trial}", participant "${participant}", and condition "${condition}"`);

    // Fetch data and plot graph
    fetch(`/data/${trial}/${participant}/${condition}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data) {
                console.log('No data received for this trial and participant');
                return;
            }

            console.log('Data received: ', data);

            const x_positions = JSON.parse(data.x_positions);
            const y_positions = JSON.parse(data.y_positions);
            const z_positions = JSON.parse(data.z_positions);
            const timestamps = JSON.parse(data.timestamps);

            
            // Assuming timestamps, x_positions, y_positions, z_positions are in arrays
            const velocities = [];
            const accelerations = [];
            const dt = timestamps[1] - timestamps[0];  // Assuming equal intervals

            for (let i = 1; i < x_positions.length; i++) {
                const dx = x_positions[i] - x_positions[i-1];
                const dy = y_positions[i] - y_positions[i-1];
                const dz = z_positions[i] - z_positions[i-1];

                const velocity = Math.sqrt(dx*dx + dy*dy + dz*dz) / dt;
                velocities.push(velocity);

                if (i > 1) {
                    const acceleration = (velocities[i-1] - velocities[i-2]) / dt;
                    accelerations.push(acceleration);
                }
            }

            // Pad first acceleration (it's not calculated for the first position)
            accelerations.unshift(accelerations[0]);


            console.log('Coordinates received: ');
            for (let i = 0; i < x_positions.length; i++) {
                console.log(`Point ${i+1}: (${x_positions[i]}, ${y_positions[i]}, ${z_positions[i]})`);
            }

            var trace1 = {
                x: x_positions,
                y: y_positions,
                z: z_positions,
                mode: 'markers',
                marker: {
                    size: 12,
                    line: {
                        color: 'rgba(217, 217, 217, 0.14)',
                        width: 0.5
                    },
                    opacity: 0.8
                },
                type: 'scatter3d'
            };

        // In your 3D plot
        var startPoint = {
            x: [x_positions[0]],
            y: [y_positions[0]],
            z: [z_positions[0]],
            mode: 'markers',
            marker: {
                size: 20,
                color: 'green',
                opacity: 1
            },
            type: 'scatter3d',
            name: 'Start'
        };

        var endPoint = {
            x: [x_positions[x_positions.length - 1]],
            y: [y_positions[y_positions.length - 1]],
            z: [z_positions[z_positions.length - 1]],
            mode: 'markers',
            marker: {
                size: 20,
                color: 'red',
                opacity: 1
            },
            type: 'scatter3d',
            name: 'End'
        };

        var data = [trace1, startPoint, endPoint];

Plotly.newPlot('plot', data, layout);
            var layout = {
                margin: {
                    l: 0,
                    r: 0,
                    b: 0,
                    t: 0
                }
            };

            Plotly.newPlot('plot', data, layout);
            plot_velocity(timestamps, velocities);
            plot_acceleration(timestamps, accelerations);

            const avg_velocity = velocities.reduce((a, b) => a + b, 0) / velocities.length;
            const avg_acceleration = accelerations.reduce((a, b) => a + b, 0) / accelerations.length;

            document.getElementById("avg-velocity").innerHTML = `Average velocity: ${avg_velocity.toFixed(2)}`;
            document.getElementById("avg-acceleration").innerHTML = `Average acceleration: ${avg_acceleration.toFixed(2)}`;

            console.log('Graph plotted successfully');

        })
        .catch(error => {
            console.error('Error fetching data: ', error);
        });
});


let currConditionIndex = 0;
let currTrialIndex = 0;

function updateSelectedOptions() {
    document.getElementById('condition-select').selectedIndex = currConditionIndex;
    document.getElementById('trial-select').selectedIndex = currTrialIndex;
    document.getElementById('go-button').click();
}

document.getElementById('forward-button').addEventListener('click', function () {
    currTrialIndex++;
    if (currTrialIndex >= document.getElementById('trial-select').length) {
        currTrialIndex = 0;
        currConditionIndex++;
        if (currConditionIndex >= document.getElementById('condition-select').length) {
            currConditionIndex = 0;
        }
    }
    updateSelectedOptions();
});

document.getElementById('backward-button').addEventListener('click', function () {
    currTrialIndex--;
    if (currTrialIndex < 0) {
        currConditionIndex--;
        if (currConditionIndex < 0) {
            currConditionIndex = document.getElementById('condition-select').length - 1;
        }
        currTrialIndex = document.getElementById('trial-select').length - 1;
    }
    updateSelectedOptions();
});

updateSelectedOptions();