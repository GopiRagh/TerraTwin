
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

const atmosphereColors = {
  earth: new THREE.Color("#459bff"),
  mars: new THREE.Color("#e87948"),
};

export default function Planet3D({ planet = "earth" }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    let animationId;
    let disposed = false;

    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(
      42,
      container.clientWidth / container.clientHeight,
      0.1,
      100
    );

    camera.position.set(0, 0, 3.2);

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;

    container.appendChild(renderer.domElement);

    // STARFIELD
    const starGeometry = new THREE.BufferGeometry();
    const starPositions = [];

    for (let i = 0; i < 1800; i++) {
      starPositions.push(
        (Math.random() - 0.5) * 65,
        (Math.random() - 0.5) * 65,
        (Math.random() - 0.5) * 65
      );
    }

    starGeometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(starPositions, 3)
    );

    const starMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.035,
      transparent: true,
      opacity: 0.8,
      sizeAttenuation: true,
    });

    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);

    // PLANET TEXTURE
    const loader = new THREE.TextureLoader();
    const texture = loader.load(
      planetTextures[planet],
      () => {
        if (!disposed) renderer.render(scene, camera);
      },
      undefined,
      (error) => console.error("Planet texture failed:", error)
    );

    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();

    const planetGeometry = new THREE.SphereGeometry(1, 128, 128);

    const planetMaterial = new THREE.MeshPhysicalMaterial({
      map: texture,
      roughness: 1,
      metalness: 0,
      clearcoat: 0,
      clearcoatRoughness: 1,
    });

    const planetMesh = new THREE.Mesh(
      planetGeometry,
      planetMaterial
    );

    // Natural axial tilt
    planetMesh.rotation.z =
      planet === "earth" ? THREE.MathUtils.degToRad(23.5) :
      planet === "mars" ? THREE.MathUtils.degToRad(25) :
      THREE.MathUtils.degToRad(6.7);

    scene.add(planetMesh);

    // ATMOSPHERIC GLOW
    let atmosphere = null;

    if (planet !== "moon") {
      const atmosphereGeometry = new THREE.SphereGeometry(
        1.045,
        96,
        96
      );

      const atmosphereMaterial = new THREE.ShaderMaterial({
        uniforms: {
          glowColor: {
            value: atmosphereColors[planet],
          },
        },

        vertexShader: `
          varying vec3 vNormal;
          varying vec3 vViewPosition;

          void main() {
            vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);

            vNormal = normalize(normalMatrix * normal);
            vViewPosition = -mvPosition.xyz;

            gl_Position = projectionMatrix * mvPosition;
          }
        `,

        fragmentShader: `
          uniform vec3 glowColor;

          varying vec3 vNormal;
          varying vec3 vViewPosition;

          void main() {
            float intensity = pow(
              1.0 - max(
                dot(normalize(vNormal), normalize(vViewPosition)),
                0.0
              ),
              3.2
            );

            gl_FragColor = vec4(
              glowColor,
              intensity * 0.65
            );
          }
        `,

        transparent: true,
        blending: THREE.AdditiveBlending,
        side: THREE.FrontSide,
        depthWrite: false,
        toneMapped: false,
      });

      atmosphere = new THREE.Mesh(
        atmosphereGeometry,
        atmosphereMaterial
      );

      scene.add(atmosphere);
    }

    // REALISTIC LIGHTING
    const ambientLight = new THREE.AmbientLight(
      0xffffff,
      planet === "moon" ? 0.35 : 0.45
    );

    scene.add(ambientLight);

    const hemisphereLight = new THREE.HemisphereLight(
      0xb9d9ff,
      0x101018,
      0.35
    );

    scene.add(hemisphereLight);

    const sunlight = new THREE.DirectionalLight(
      0xffffff,
      3.2
    );

    sunlight.position.set(5, 2.5, 5);
    scene.add(sunlight);

    const rimLight = new THREE.DirectionalLight(
      planet === "mars" ? 0xff9568 : 0x559bff,
      0.35
    );

    rimLight.position.set(-4, 0, -3);
    scene.add(rimLight);

    // CAMERA CONTROLS
    const controls = new OrbitControls(
      camera,
      renderer.domElement
    );

    controls.enableDamping = true;
    controls.dampingFactor = 0.045;
    controls.enablePan = false;
    controls.minDistance = 1.7;
    controls.maxDistance = 5;
    controls.rotateSpeed = 0.55;

    // ANIMATION
    const clock = new THREE.Clock();

    const animate = () => {
      animationId = requestAnimationFrame(animate);

      const delta = Math.min(clock.getDelta(), 0.05);

      planetMesh.rotation.y += delta * 0.12;

      if (atmosphere) {
        atmosphere.rotation.y += delta * 0.12;
      }

      stars.rotation.y += delta * 0.002;

      controls.update();
      renderer.render(scene, camera);
    };

    animate();

    // RESPONSIVE CANVAS
    const resizeObserver = new ResizeObserver(() => {
      const width = container.clientWidth;
      const height = container.clientHeight;

      if (!width || !height) return;

      camera.aspect = width / height;
      camera.updateProjectionMatrix();

      renderer.setSize(width, height);
    });

    resizeObserver.observe(container);

    // CLEANUP
    return () => {
      disposed = true;

      cancelAnimationFrame(animationId);
      resizeObserver.disconnect();
      controls.dispose();

      planetGeometry.dispose();
      planetMaterial.dispose();
      texture.dispose();

      starGeometry.dispose();
      starMaterial.dispose();

      if (atmosphere) {
        atmosphere.geometry.dispose();
        atmosphere.material.dispose();
      }

      renderer.dispose();

      if (renderer.domElement.parentNode === container) {
        container.removeChild(renderer.domElement);
      }
    };
  }, [planet]);

  return <div ref={mountRef} className="planet-canvas" />;
}
