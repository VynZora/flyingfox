import * as THREE from "three";

import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

/* ======================================================
   CONTAINER
====================================================== */

const container = document.getElementById("three-container");

/* ======================================================
   SCENE
====================================================== */

const scene = new THREE.Scene();

/* ======================================================
   CAMERA
====================================================== */

const camera = new THREE.PerspectiveCamera(
  40,

  window.innerWidth / window.innerHeight,

  0.1,

  1000,
);

camera.position.set(0, 0, 12);

camera.lookAt(0, 0, 0);

/* ======================================================
   RENDERER
====================================================== */

const renderer = new THREE.WebGLRenderer({
  antialias: true,

  alpha: true,
});

renderer.setSize(
  window.innerWidth,

  window.innerHeight,
);

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

renderer.outputColorSpace = THREE.SRGBColorSpace;

renderer.setClearColor(0x000000, 0);

container.appendChild(renderer.domElement);

/* ======================================================
   LIGHTING
====================================================== */

const ambientLight = new THREE.AmbientLight(
  0xffffff,

  3,
);

scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(
  0xffffff,

  4,
);

directionalLight.position.set(5, 8, 10);

scene.add(directionalLight);

/* ======================================================
   ZIPLINE

   START = RIGHT SIDE
   END   = LEFT SIDE
====================================================== */

const cableStart = new THREE.Vector3(
  7.5,

  2.8,

  0,
);

const cableEnd = new THREE.Vector3(
  -7.5,

  -1.3,

  0,
);

/* STRAIGHT LINE */

const cableCurve = new THREE.LineCurve3(
  cableStart,

  cableEnd,
);

/* ======================================================
   CABLE MESH
====================================================== */

const cableGeometry = new THREE.TubeGeometry(
  cableCurve,

  64,

  0.018,

  8,

  false,
);

const cableMaterial = new THREE.MeshStandardMaterial({
  color: 0x151515,

  metalness: 0.7,

  roughness: 0.35,
});

const cable = new THREE.Mesh(
  cableGeometry,

  cableMaterial,
);

scene.add(cable);

/* ======================================================
   RIDER HOLDER

   THIS object moves along the cable.
====================================================== */

const riderHolder = new THREE.Group();

scene.add(riderHolder);

/* ======================================================
   LOAD RIDER
====================================================== */

const loader = new GLTFLoader();

loader.load(
  window.RIDER_MODEL_URL,

  function (gltf) {
    const rider = gltf.scene;

    /* ==============================================
           RIDER SIZE
        ============================================== */

    rider.scale.set(
      2.8,

      2.8,

      2.8,
    );

    /* ==============================================
           IMPORTANT

           Move model DOWN from cable.

           The holder itself stays ON the cable.
        ============================================== */

    rider.position.set(
      0,

      -2.4,

      0,
    );

    /* ==============================================
           RIDER DIRECTION

           Test this value if necessary.
        ============================================== */

    rider.rotation.y = -Math.PI / 2;

    rider.traverse(function (child) {
      if (child.isMesh) {
        child.castShadow = true;

        child.receiveShadow = true;
      }
    });

    riderHolder.add(rider);

    console.log("Rider loaded");
  },

  undefined,

  function (error) {
    console.error(
      "Rider loading error:",

      error,
    );
  },
);

/* ======================================================
   START POSITION

   0 = RIGHT SIDE

   1 = LEFT SIDE
====================================================== */

const riderProgress = {
  value: 0.05,
};

/* ======================================================
   GSAP
====================================================== */

gsap.registerPlugin(ScrollTrigger);

/* ======================================================
   SCROLL RIDER

   RIGHT
        ↓
   CENTER
        ↓
   LEFT
====================================================== */

gsap.to(
  riderProgress,

  {
    value: 0.95,

    ease: "none",

    scrollTrigger: {
      trigger: ".hero-section",

      start: "top top",

      end: "+=1800",

      scrub: 1,

      pin: true,
    },
  },
);

/* ======================================================
   UPDATE RIDER
====================================================== */

function updateRider() {
  const position = cableCurve.getPoint(riderProgress.value);

  riderHolder.position.copy(position);
}

/* ======================================================
   ANIMATION
====================================================== */

function animate() {
  requestAnimationFrame(animate);

  updateRider();

  renderer.render(
    scene,

    camera,
  );
}

animate();

/* ======================================================
   RESIZE
====================================================== */

window.addEventListener(
  "resize",

  function () {
    camera.aspect = window.innerWidth / window.innerHeight;

    camera.updateProjectionMatrix();

    renderer.setSize(
      window.innerWidth,

      window.innerHeight,
    );

    renderer.setPixelRatio(
      Math.min(
        window.devicePixelRatio,

        2,
      ),
    );
  },
);
