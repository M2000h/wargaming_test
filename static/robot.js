import * as THREE from 'three';
import {GLTFLoader} from 'gltf';
import {OrbitControls} from 'controls';

init("container", 'Walking');
init("win_container", 'Dance');
init("draw_container", 'Idle');
init("lose_container", 'Death', false);

function init(container_id, action, repeat = true) {
    let container, clock, mixer, activeAction;
    let camera, scene, renderer, model, controls;

    container = document.getElementById(container_id);

    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.25, 100);
    camera.position.set(-5, 3, 10);
    camera.lookAt(0, 2, 0);

    scene = new THREE.Scene();

    clock = new THREE.Clock();

    const hemiLight = new THREE.HemisphereLight(0xffffff, 0x8d8d8d, 3);
    hemiLight.position.set(0, 20, 0);
    scene.add(hemiLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 3);
    dirLight.position.set(0, 20, 10);
    scene.add(dirLight);

    renderer = new THREE.WebGLRenderer({antialias: true, alpha: true});
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);
    renderer.setClearColor(0x000000, 0);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.target = new THREE.Vector3(0, 2, 0);

    window.addEventListener('resize', function () {
        onWindowResize(renderer, camera, container)
    });
    setInterval(function () {
        onWindowResize(renderer, camera, container)
    }, 100);


    const loader = new GLTFLoader();
    loader.load('https://threejs.org/examples/models/gltf/RobotExpressive/RobotExpressive.glb', function (gltf) {
        model = gltf.scene;
        scene.add(model);
        mixer = createGUI(model, gltf.animations, activeAction, action, repeat);
        animate(clock, renderer, mixer, scene, camera, controls);
    }, undefined, function (e) {
        console.error(e);
    });

}

function createGUI(model, animations, activeAction, action, repeat) {
    let mixer = new THREE.AnimationMixer(model);

    let actions = {};

    for (let i = 0; i < animations.length; i++) {
        const clip = animations[i];
        actions[clip.name] = mixer.clipAction(clip);
    }
    activeAction = actions[action];
    if (!repeat) {
        activeAction.clampWhenFinished = true;
        activeAction.loop = THREE.LoopOnce;
    }
    activeAction.play();
    return mixer;
}

function onWindowResize(renderer, camera, container) {
    let width = container.clientWidth;
    let height = container.clientHeight;

    renderer.setSize(width, height);

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate(clock, renderer, mixer, scene, camera, controls) {
    const dt = clock.getDelta();

    if (mixer) mixer.update(dt);
    controls.update();
    requestAnimationFrame(function () {
        animate(clock, renderer, mixer, scene, camera, controls)
    });

    renderer.render(scene, camera);
}
