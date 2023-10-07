import * as THREE from 'three';
import {GLTFLoader} from 'gltf';
import {OrbitControls} from 'controls';


let container, clock, mixer, actions, activeAction, previousAction;
let camera, scene, renderer, model, face, controls;
init();
animate();

function init() {
    container = document.getElementById('lose_container');

    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.25, 100);
    camera.position.set(-5, 3, 10);
    camera.lookAt(0, 2, 0);


    scene = new THREE.Scene();

    clock = new THREE.Clock();

    // lights

    const hemiLight = new THREE.HemisphereLight(0xffffff, 0x8d8d8d, 3);
    hemiLight.position.set(0, 20, 0);
    scene.add(hemiLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 3);
    dirLight.position.set(0, 20, 10);
    scene.add(dirLight);


    const loader = new GLTFLoader();
    loader.load('https://threejs.org/examples/models/gltf/RobotExpressive/RobotExpressive.glb', function (gltf) {
        model = gltf.scene;
        scene.add(model);
        createGUI(model, gltf.animations);
    }, undefined, function (e) {
        console.error(e);
    });

    renderer = new THREE.WebGLRenderer({antialias: true, alpha: true});
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);
    renderer.setClearColor(0x000000, 0);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.target = new THREE.Vector3(0, 2, 0);

    window.addEventListener('resize', onWindowResize);
    setInterval(onWindowResize, 100);
}

function createGUI(model, animations) {
    mixer = new THREE.AnimationMixer(model);

    actions = {};

    for (let i = 0; i < animations.length; i++) {
        const clip = animations[i];
        actions[clip.name] = mixer.clipAction(clip);
    }
    face = model.getObjectByName('Head_4');
    activeAction = actions['Death'];
    activeAction.clampWhenFinished = true;
    activeAction.loop = THREE.LoopOnce;
    activeAction.play();
}

function onWindowResize() {
    let width = container.clientWidth;
    let height = container.clientHeight;
    renderer.setSize(width, height);

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {

    const dt = clock.getDelta();

    if (mixer) mixer.update(dt);
    controls.update();
    requestAnimationFrame(animate);

    renderer.render(scene, camera);

}