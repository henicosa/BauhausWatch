var inputLength;
// Set up the scene
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
var renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0xffffff, 0); // Set background color to white
document.getElementById('animation').appendChild(renderer.domElement);

// Create blue material
var blueMaterial = new THREE.MeshStandardMaterial({ color: 0x0000ff });

// Create red material
var redMaterial = new THREE.MeshStandardMaterial({ color: 0xff0000 });

// Create yellow material
var yellowMaterial = new THREE.MeshStandardMaterial({ color: 0xffff00 });


var greyMaterial = new THREE.MeshStandardMaterial({ color: 0x999999 });

var starTypes = {
    "sphere": new THREE.SphereGeometry(0.1, 16, 16), 
    "cube": new THREE.BoxGeometry(0.1, 0.1, 0.1),
    "cone": new THREE.ConeGeometry(0.1, 0.2, 32)
};

var starMaterials = {
    "sphere": blueMaterial,
    "cube": redMaterial,
    "cone": yellowMaterial
}

// Create spheres (stars)
var fieldOfView = 20;
var numStars = 150;
var stars = [];
var speedFactor = 0.03;
var levels = generateNumbersWithDistribution(numStars);


var keys = Object.keys(starTypes);

for (var i = 0; i < numStars; i++) {

    var randomStarType = keys[Math.floor(Math.random() * 3)];
    var star = {};
    star["level"] = levels[i]
    var mesh = new THREE.Mesh(starTypes[randomStarType], starMaterials[randomStarType]);

    if (randomStarType == "cone") {
        random_rotate(mesh);
    }
    random_place(mesh, fieldOfView);
    star["object"] = mesh;
    star["material"] = mesh.material;

    scene.add(star["object"]);
    stars.push(star);
}

// Add a light in the top-left corner
var light = new THREE.PointLight(0xffffff, 1000, 100);
light.position.set(-10, 10, 10);
scene.add(light);

// set ambient light
var ambientLight = new THREE.AmbientLight(0x404040, 10);
scene.add(ambientLight);


// Position the camera
camera.position.z = 5;

// Create a function to animate the stars and move the camera
function animate() {
    requestAnimationFrame(animate);

    // Get the input element
    var inputElement = document.querySelector('.searchTerm');

    // Get the length of the entered text
    inputLength = inputElement.value.length;


    // Process the stars
    stars.forEach(x => processStars(x, inputLength))

    renderer.render(scene, camera);

}

// Call the animate function
animate();

// Handle window resize
window.addEventListener('resize', function () {
    const newWidth = window.innerWidth;
    const newHeight = window.innerHeight;

    // Update renderer size
    renderer.setSize(newWidth, newHeight);

    // Update camera aspect ratio
    camera.aspect = newWidth / newHeight;
    camera.updateProjectionMatrix();
});

function processStars(star, inputLength) {
    if (inputLength >= star["level"]) {
        star["object"].material = greyMaterial;
    } else {
        star["object"].material = star["material"]
    }


    star["object"].rotation.x += 0.005;
    star["object"].rotation.y += 0.005;
    star["object"].position.z += (0.005 + (Math.abs(star["object"].position.x) + Math.abs(star["object"].position.y)) / (fieldOfView * 4)) * speedFactor; //- 1/(2*(star.position.z-15));

    // if star is not in the field of view, move it to the other side
    if (star["object"].position.z > fieldOfView / 2) {
        star["object"].position.z = -fieldOfView / 2;
    }
}

function generateNumbersWithDistribution(n) {
    if (n <= 0) {
        console.error("Please provide a positive value for n.");
        return [];
    }

    const result = [];
    let currentNumber = 1;

    for (let i = 0; i < n; i++) {
        
        var rounds = 1
        // Increase the likelihood of the next number being the same

        while (rounds < 10 && Math.random() < 0.7)
            rounds += 1;

        result.push(rounds)

        // Otherwise, move to the next number (up to 10)
        currentNumber = Math.min(10, currentNumber + 1);
    }

    var occurrences = result.reduce(function (obj, item) {
        obj[item] = (obj[item] || 0) + 1;
        return obj;
    }, {});

    console.log(occurrences)


    return result;
}

function random_place(mesh, range) {
    mesh.position.x = (Math.random() - 0.5) * range;
    mesh.position.y = (Math.random() - 0.5) * range;
    mesh.position.z = (Math.random() - 0.5) * range;
}

function random_rotate(mesh) {
    mesh.rotation.x = (Math.random() - 0.5);
    mesh.rotation.y = (Math.random() - 0.5);
    mesh.rotation.z = (Math.random() - 0.5);
}

function start_lookup_animation() {
    speedFactor = 0.6;
}

function stop_lookup_animation() {
  speedFactor = 0.03;
}
