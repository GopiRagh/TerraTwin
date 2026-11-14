
import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

import earthTexture from "../assets/textures/earth.jpg";
import moonTexture from "../assets/textures/moon.jpg";
import marsTexture from "../assets/textures/mars.jpg";

const planetTextures = {
  earth: earthTexture,
  moon: moonTexture,
  mars: marsTexture,
};

export default function Planet3D({ planet = "earth" }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(
      45,
      container.clientWidth / container.clientHeight,
      0.1,
      100
    );
    camera.position.z = 3.2;

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
    });

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.appendChild(renderer.domElement);

    // Stars
    const starGeometry = new THREE.BufferGeometry();
    const starPositions = [];

    for (let i = 0; i < 1200; i++) {
      starPositions.push(
        (Math.random() - 0.5) * 60,
        (Math.random() - 0.5) * 60,
        (Math.random() - 0.5) * 60
      );
    }

    starGeometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(starPositions, 3)
    );

    const starMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.045,
    });

    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);

    // Planet texture
    const loader = new THREE.TextureLoader();

    let texture;
    let sphere;
    let animationId;

    texture = loader.load(
      planetTextures[planet],
      () => {
        texture.colorSpace = THREE.SRGBColorSpace;
        texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
        renderer.render(scene, camera);
      },
      undefined,
      (error) => console.error("Planet texture failed to load:", error)
    );

    const geometry = new THREE.SphereGeometry(1, 96, 96);

    const material = new THREE.MeshStandardMaterial({
      map: texture,
      roughness: 1,
      metalness: 0,
    });

    sphere = new THREE.Mesh(geometry, material);
    scene.add(sphere);

    // Lighting
    scene.add(new THREE.AmbientLight(0xffffff, 1.5));

    const sunlight = new THREE.DirectionalLight(0xffffff, 2.5);
    sunlight.position.set(5, 3, 5);
    scene.add(sunlight);

    const fillLight = new THREE.DirectionalLight(0x8bbcff, 0.5);
    fillLight.position.set(-5, 0, -4);
    scene.add(fillLight);

    // Rotation and zoom controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 1.5;
    controls.maxDistance = 5;

    const animate = () => {
      animationId = requestAnimationFrame(animate);

      if (sphere) {
        sphere.rotation.y += 0.0015;
      }

      controls.update();
      renderer.render(scene, camera);
    };

    animate();

    // Responsive sizing
    const resizeObserver = new ResizeObserver(() => {
      const width = container.clientWidth;
      const height = container.clientHeight;

      if (!width || !height) return;

      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    });

    resizeObserver.observe(container);

    return () => {
      cancelAnimationFrame(animationId);
      resizeObserver.disconnect();
      controls.dispose();
      geometry.dispose();
      material.dispose();
      texture.dispose();
      starGeometry.dispose();
      starMaterial.dispose();
      renderer.dispose();

      if (renderer.domElement.parentNode === container) {
        container.removeChild(renderer.domElement);
      }
    };
  }, [planet]);

  return <div ref={mountRef} className="planet-canvas" />;
}
