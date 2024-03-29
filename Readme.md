## Evolving objects overview

program is run: **python3 evolution.py**

There are four main criteria for evaluation: **efficiency**, **illuminance uniformity**, **glare reduction** and **light pollution**

user can set program parameters and evaluation criteria in file **parameters.json**

### Examples
There are examples for each criterion:

#### Used parameters
`{
    "lamp": {
        "number_of_rays": 20,
	"ray_distribution": "uniform",
        "base_length": 200,
        "base_angle": 15,
        "angle_lower_bound": 90,
        "angle_upper_bound": 180,
        "length_lower_bound": 1,
        "length_upper_bound": 3
        },
    "road": {
        "start": -1000,
        "end": 10000, 
	"depth": -8000,
	"sections": 4
    },
    "evolution": {
        "population_size": 10,
        "number_of_generations": 100,
        "operators": {
            "mutation": {
                "angle_mutation_prob": 0.4,
                "length_mutation_prob": 0.4
            },
            "xover_prob": 0
        }
    },
    "evaluation": {
	"reflective_factor" : 0.98,
	"inverse_square_law": "No",
	"cosine_error": "No",
        "criterion": "efficiency"
    }
}`

#### Glare reduction

<img src="stats/glare_reduction.svg" alt="drawing" width="600"/>

<img src="stats/img-best50_glare_reduction.png" alt="drawing" width="600"/>


#### Efficiency

<img src="stats/efficiency.svg" alt="drawing" width="600"/>

<img src="stats/img-best50_efficiency.png" alt="drawing" width="600"/>


#### Light pollution

<img src="stats/light_pollution.svg" alt="drawing" width="600"/>

<img src="stats/img-best60_light_pollution.png" alt="drawing" width="600"/>


#### Illuminance uniformity

<img src="stats/illuminance_uniformity.svg" alt="drawing" width="600"/>

<img src="stats/img-best50_illuminance_uniformity.png" alt="drawing" width="600"/>


## Evolving objects  - 3D model

- first attempts with 3D model


<img src="stats/random.png" alt="drawing" width="600"/>
<img src="stats/random2.png" alt="drawing" width="600"/>
<img src="stats/uniform.png" alt="drawing" width="600"/>

- reflection from one plane

<img src="stats/reflection.png" alt="drawing" width="600"/>



