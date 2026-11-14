
import { useState } from "react";
import Planet3D from "../components/Planet3D";
import "./PlanetShowcase.css";

const planets = [
  {
    id: "earth",
    name: "Earth",
    number: "01",
    description: "Explore Earth's terrain, climate and environmental conditions.",
  },
  {
    id: "moon",
    name: "Moon",
    number: "02",
    description: "Explore lunar craters, elevation and polar regions.",
  },
  {
    id: "mars",
    name: "Mars",
    number: "03",
    description: "Explore Martian landscapes, topography and thermal patterns.",
  },
];

export default function PlanetShowcase() {
  const [selected, setSelected] = useState(0);

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({
      behavior: "smooth",
    });
  };

  return (
    <div className="terra-dashboard">

      {/* NAVIGATION */}
      <header className="terra-nav">
        <div className="terra-brand">
          <div className="terra-logo">◎</div>
          <div>
            <h2>TERRATWIN</h2>
            <small>PLANETARY ANALOG RESEARCH</small>
          </div>
        </div>

        <nav className="terra-links">
          <button onClick={() => scrollTo("dashboard")}>Dashboard</button>
          <button onClick={() => scrollTo("earth-analogs")}>Earth Analogs</button>
          <button onClick={() => {
            setSelected(1);
            scrollTo("planet-explorer");
          }}>Moon Research</button>
          <button onClick={() => {
            setSelected(2);
            scrollTo("planet-explorer");
          }}>Mars Research</button>
          <button onClick={() => scrollTo("planet-explorer")}>Compare</button>
        </nav>
      </header>

      <main id="dashboard">

        {/* HERO SECTION */}
        <section className="terra-hero">

          <div className="hero-content">
            <div className="terra-label">
              <span className="status-dot"></span>
              PLANETARY RESEARCH PLATFORM
            </div>

            <h1>
              Explore. Discover.
              <br />
              <span>Find Earth's Planetary Twins.</span>
            </h1>

            <p>
              An interactive Earth–Moon–Mars environment for exploring
              planetary surfaces, comparing scientific parameters and
              discovering terrestrial analog locations.
            </p>

            <div className="terra-actions">
              <button
                className="primary-action"
                onClick={() => scrollTo("earth-analogs")}
              >
                EXPLORE EARTH ANALOGS ↗
              </button>

              <button
                className="secondary-action"
                onClick={() => scrollTo("planet-explorer")}
              >
                COMPARE PLANETS ◎
              </button>
            </div>
          </div>

          {/* PLANETARY VISUAL */}
          <div className="hero-space">

            <div className="space-stars"></div>

            <div className="hero-orbit orbit-one"></div>
            <div className="hero-orbit orbit-two"></div>
            <div className="hero-orbit orbit-three"></div>

            <div className="hero-earth">
              <Planet3D planet="earth" />
            </div>

            <div className="hero-moon">
              <Planet3D planet="moon" />
            </div>

            <div className="hero-mars">
              <Planet3D planet="mars" />
            </div>

            <div className="planet-tag earth-tag">
              <small>PRIMARY PLANET</small>
              <strong>EARTH</strong>
            </div>

            <div className="planet-tag moon-tag">
              <small>REFERENCE BODY</small>
              <strong>MOON</strong>
            </div>

            <div className="planet-tag mars-tag">
              <small>REFERENCE BODY</small>
              <strong>MARS</strong>
            </div>

            <div className="space-caption">
              EARTH · MOON · MARS
            </div>

          </div>

        </section>

        {/* RESEARCH STATUS PANELS */}
        <section className="terra-stats" id="earth-analogs">

          <div className="stat-card">
            <div className="stat-icon blue-icon">◉</div>
            <small>PLANETARY BODIES</small>
            <h2>03</h2>
            <p>Earth · Moon · Mars</p>
          </div>

          <div className="stat-card">
            <div className="stat-icon purple-icon">▤</div>
            <small>DATA INTEGRATION</small>
            <h2>NASA</h2>
            <p>Scientific dataset workspace</p>
          </div>

          <div className="stat-card">
            <div className="stat-icon green-icon">⌁</div>
            <small>ANALYSIS MODULES</small>
            <h2>03</h2>
            <p>Terrain · Thermal · Geology</p>
          </div>

          <div className="stat-card">
            <div className="stat-icon orange-icon">⌖</div>
            <small>ANALOG EXPLORATION</small>
            <h2>READY</h2>
            <p>Awaiting site dataset integration</p>
          </div>

        </section>

        {/* PLANET EXPLORER */}
        <section className="planet-explorer" id="planet-explorer">

          <div className="section-heading">
            <small>PLANETARY DATA EXPLORER</small>
            <h2>Explore the Three Worlds</h2>
            <p>Select a planetary body to explore its 3D surface.</p>
          </div>

          <div className="planet-tabs">
            {planets.map((item, index) => (
              <button
                key={item.id}
                className={selected === index ? "active" : ""}
                onClick={() => setSelected(index)}
              >
                {item.name}
              </button>
            ))}
          </div>

          <div className="selected-planet">

            <div className="planet-view">
              <Planet3D
                key={planets[selected].id}
                planet={planets[selected].id}
              />
            </div>

            <div className="selected-planet-info">
              <small>
                PLANETARY BODY {planets[selected].number}
              </small>

              <h3>{planets[selected].name}</h3>

              <p>{planets[selected].description}</p>

              <p>NASA planetary imagery and surface exploration.</p>

              <div className="explorer-status">
                <span className="status-dot"></span>
                3D SURFACE VIEW ACTIVE
              </div>
            </div>

          </div>
        </section>

      </main>

      <footer className="terra-footer">
        TERRATWIN · EARTH–MOON–MARS ANALOG EXPLORATION PLATFORM
      </footer>

    </div>
  );
}
