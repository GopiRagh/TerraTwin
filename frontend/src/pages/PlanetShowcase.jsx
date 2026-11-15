import { lazy, Suspense, useEffect, useMemo, useRef, useState } from "react";
import { Activity, ArrowDownRight, ArrowRight, Bot, Crosshair, Database, MapPin, Orbit, Radio, Send, SatelliteDish, Sparkles, X } from "lucide-react";
import { api } from "../services/api";
import "./PlanetShowcase.css";

const Planet3D = lazy(() => import("../components/Planet3D"));
const AnalogMap = lazy(() => import("../components/AnalogMap"));

const descriptions = {
  earth: "Our reference world. Explore the landscapes and conditions that help researchers find planetary analogs.",
  moon: "A stark, cratered landscape shaped by impact and time. Compare lunar terrain against Earth's most similar environments.",
  mars: "A cold desert world with a rich geological record. Explore its surface and search for Earth analog terrain.",
};

function siteSlug(location) {
  return location.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
}

function ErrorNotice({ children }) {
  return children ? <p className="api-error" role="alert">{children}</p> : null;
}

export default function PlanetShowcase() {
  const [planets, setPlanets] = useState([]);
  const [locations, setLocations] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [earthCandidates, setEarthCandidates] = useState([]);
  const [earthCandidateError, setEarthCandidateError] = useState("");
  const [selected, setSelected] = useState("earth");
  const [targetPlanet, setTargetPlanet] = useState("moon");
  const [targetLocation, setTargetLocation] = useState("");
  const [focusedEarthSite, setFocusedEarthSite] = useState("");
  const [comparison, setComparison] = useState(null);
  const [analysisStarted, setAnalysisStarted] = useState(false);
  const [apiStatus, setApiStatus] = useState("connecting");
  const [loading, setLoading] = useState(true);
  const [locationError, setLocationError] = useState("");
  const [compareError, setCompareError] = useState("");
  const [comparing, setComparing] = useState(false);
  const [globeReady, setGlobeReady] = useState(false);
  const [mapOpen, setMapOpen] = useState(true);
  const [visualizedMatch, setVisualizedMatch] = useState("");
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [assistantStatus, setAssistantStatus] = useState("idle");
  const [chatMessages, setChatMessages] = useState([]);
  const [chatDraft, setChatDraft] = useState("");
  const [chatSending, setChatSending] = useState(false);
  const [chatError, setChatError] = useState("");
  const [activeNav, setActiveNav] = useState("dashboard");
  const chatEndRef = useRef(null);

  useEffect(() => {
    const sectionIds = ["dashboard", "planet-explorer", "earth-analogs", "analog-comparison"];
    const sections = sectionIds.map((id) => document.getElementById(id)).filter(Boolean);
    if (!sections.length || !("IntersectionObserver" in window)) return undefined;
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting);
      if (visible.length) {
        visible.sort((first, second) => second.intersectionRatio - first.intersectionRatio);
        setActiveNav(visible[0].target.id);
      }
    }, { rootMargin: "-22% 0px -62% 0px", threshold: [0, 0.1, 0.3] });
    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!assistantOpen) return undefined;
    let active = true;
    api.assistantHealth()
      .then(() => active && setAssistantStatus("online"))
      .catch(() => active && setAssistantStatus("offline"));
    return () => { active = false; };
  }, [assistantOpen]);

  useEffect(() => {
    if (assistantOpen) chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [assistantOpen, chatMessages, chatSending]);

  useEffect(() => {
    const timer = window.setTimeout(() => setGlobeReady(true), 250);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    let active = true;
    Promise.allSettled([api.health(), api.planets(), api.datasets(), api.earthCandidates()]).then((results) => {
      if (!active) return;
      const [health, planetResult, datasetResult, candidateResult] = results;
      setApiStatus(health.status === "fulfilled" ? "online" : "offline");
      if (planetResult.status === "fulfilled") {
        const data = planetResult.value.data || [];
        setPlanets(data);
        if (data.length) setSelected((current) =>
          data.some((planet) => planet.id === current) ? current : data[0].id,
        );
      }
      if (datasetResult.status === "fulfilled") setDatasets(datasetResult.value.data || []);
      if (candidateResult.status === "fulfilled") {
        setEarthCandidates(candidateResult.value.data || []);
        setEarthCandidateError("");
      } else {
        setEarthCandidateError(candidateResult.reason?.message || "Could not load the Earth reference locations.");
      }
      setLoading(false);
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    let active = true;
    api.locations(targetPlanet).then((result) => {
      if (!active) return;
      const data = result.data || [];
      setLocations(data);
      setTargetLocation((current) =>
        data.some((location) => location.name === current) ? current : data[0]?.name || "",
      );
    }).catch((error) => {
      if (!active) return;
      setLocations([]);
      setLocationError(error.message);
    });
    return () => { active = false; };
  }, [targetPlanet]);

  const selectedPlanet = planets.find((planet) => planet.id === selected);
  const visibleDatasets = useMemo(
    () => datasets.filter((dataset) => dataset.planet === selected),
    [datasets, selected],
  );
  const datasetCategories = useMemo(
    () => [...new Set(visibleDatasets.map((dataset) => dataset.category))],
    [visibleDatasets],
  );
  const [datasetSearch, setDatasetSearch] = useState("");
  const [datasetCategory, setDatasetCategory] = useState("all");
  const filteredDatasets = useMemo(() => {
    const term = datasetSearch.trim().toLowerCase();
    return visibleDatasets.filter((dataset) => {
      const matchesCategory = datasetCategory === "all" || dataset.category === datasetCategory;
      const searchText = [dataset.name, dataset.dataset_id, dataset.instrument, dataset.provider, dataset.purpose, ...(dataset.local_files || [])].join(" ").toLowerCase();
      return matchesCategory && (!term || searchText.includes(term));
    });
  }, [datasetCategory, datasetSearch, visibleDatasets]);
  const bestVisualMatch = comparison?.results?.find((result) => result.location === visualizedMatch)
    || comparison?.results?.find((result) => result.location === focusedEarthSite)
    || comparison?.results?.[0];
  const rankedEarthSites = new Map((comparison?.results || []).map((result) => [result.location, result]));
  const targetImageNames = {
    "Jezero Crater": "mars_jezero",
    "Shackleton Crater": "moon_shackleton",
  };
  const targetTerrain = {
    body: `${targetPlanet.toUpperCase()} / ${targetLocation.toUpperCase()}`,
    image: `/analogs/targets/${targetImageNames[targetLocation] || siteSlug(targetLocation)}.png`,
    source: targetPlanet === "moon" ? "LOLA GLOBAL DEM ? ~1.9 KM / PIXEL" : "MOLA MEGDR ? ~3.7 KM / PIXEL",
  };

  const scrollTo = (id) => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });

  const clearAnalysis = () => {
    setAnalysisStarted(false);
    setComparison(null);
    setCompareError("");
    setVisualizedMatch("");
    setFocusedEarthSite("");
    setMapOpen(true);
  };

  const runComparison = async (event) => {
    event.preventDefault();
    setAnalysisStarted(true);
    setCompareError("");
    setComparison(null);
    setVisualizedMatch("");
    setComparing(true);
    try {
      const response = await api.compare(targetPlanet, targetLocation.trim());
      setComparison(response.data);
    } catch (error) {
      setCompareError(error.message);
    } finally {
      setComparing(false);
    }
  };

  const retryEarthCandidates = async () => {
    setEarthCandidateError("");
    try {
      const result = await api.earthCandidates();
      setEarthCandidates(result.data || []);
    } catch (error) {
      setEarthCandidateError(error.message);
    }
  };

  const sendAssistantMessage = async (eventOrMessage) => {
    if (typeof eventOrMessage !== "string") eventOrMessage?.preventDefault();
    const message = (typeof eventOrMessage === "string" ? eventOrMessage : chatDraft).trim();
    if (!message || chatSending) return;
    const history = chatMessages.slice(-8).map(({ role, content }) => ({ role, content }));
    const makeId = () => `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    setChatMessages((current) => [...current, { id: makeId(), role: "user", content: message }]);
    setChatDraft("");
    setChatError("");
    setChatSending(true);
    try {
      const result = await api.assistantChat(message, history);
      setChatMessages((current) => [...current, { id: makeId(), role: "assistant", content: result.reply || "I couldn't prepare a response. Please try again.", comparison: result.comparison }]);
      setAssistantStatus("online");
    } catch (error) {
      setAssistantStatus("offline");
      setChatError(error.message);
    } finally {
      setChatSending(false);
    }
  };

  const connectionLabel = apiStatus === "online" ? "SYSTEMS NOMINAL" : apiStatus === "offline" ? "API OFFLINE" : "CONNECTING";

  return (
    <div className="terra-dashboard">
      <a className="skip-link" href="#main-content">Skip to content</a>
      <header className="terra-nav">
        <button className="terra-brand" onClick={() => scrollTo("dashboard")} aria-label="TerraTwin home">
          <span className="brand-mark"><Orbit size={21} strokeWidth={1.6} /></span>
          <span className="brand-wordmark"><strong>TERRA<span>TWIN</span></strong><small>PLANETARY ANALOG RESEARCH</small></span>
        </button>
        <nav className="terra-links" aria-label="Main navigation">
          <button className={activeNav === "dashboard" ? "nav-active" : ""} aria-current={activeNav === "dashboard" ? "page" : undefined} onClick={() => scrollTo("dashboard")}>Overview</button>
          <button className={activeNav === "planet-explorer" ? "nav-active" : ""} aria-current={activeNav === "planet-explorer" ? "page" : undefined} onClick={() => scrollTo("planet-explorer")}>Worlds</button>
          <button className={activeNav === "earth-analogs" ? "nav-active" : ""} aria-current={activeNav === "earth-analogs" ? "page" : undefined} onClick={() => scrollTo("earth-analogs")}>Data library</button>
          <button className={activeNav === "analog-comparison" ? "nav-active" : ""} aria-current={activeNav === "analog-comparison" ? "page" : undefined} onClick={() => scrollTo("analog-comparison")}>Analog finder</button>
        </nav>
        <div className="terra-nav-actions">
          <button className={`assistant-trigger ${assistantOpen ? "active" : ""}`} onClick={() => { if (!assistantOpen) setAssistantStatus("checking"); setAssistantOpen(!assistantOpen); }} aria-expanded={assistantOpen} aria-label={assistantOpen ? "Close TerraTwin AI assistant" : "Open TerraTwin AI assistant"}><Bot size={15} /><span>AI ASSISTANT</span><Sparkles size={12} /></button>
          <div className={`connection-pill ${apiStatus}`}><span className="connection-light" />{connectionLabel}</div>
        </div>
      </header>

      <main id="main-content">
        <section className="terra-hero" id="dashboard">
          <div className="hero-backdrop" aria-hidden="true"><div className="hero-grid" /><div className="hero-nebula" /></div>
          <div className="hero-content">
            <div className="hero-kicker"><span className="kicker-line" /> PLANETARY OBSERVATION NETWORK <span className="kicker-index">TT / 01</span></div>
            <h1>Worlds<br />in <span>perspective.</span></h1>
            <p>Explore distant terrain. Find the places on Earth that tell us what other worlds are like.</p>
            <button className="hero-cta" onClick={() => scrollTo("analog-comparison")}>Begin an analysis <ArrowDownRight size={17} /></button>
            <div className="hero-footnote"><Crosshair size={13} /><span>ELEVATION-BASED ANALOG DISCOVERY</span><span className="footnote-divider" /><span>EARTH / MOON / MARS</span></div>
          </div>

          <div className="hero-space" aria-label={`${selectedPlanet?.name || "Earth"} interactive 3D model`}>
            <div className="space-stars" />
            <div className="hero-orbit orbit-one" /><div className="hero-orbit orbit-two" /><div className="hero-orbit orbit-three" />
            <div className="orbit-crosshair crosshair-top" /><div className="orbit-crosshair crosshair-bottom" />
            <div className="hero-earth">
              {globeReady ? <Suspense fallback={<div className="globe-loading" />}><Planet3D key={selected} planet={selected} /></Suspense> : <div className="globe-loading" />}
            </div>
            <div className="globe-label label-top"><span className="label-mark" /> ORBITAL VIEW <span>LIVE</span></div>
            <div className="globe-label label-bottom"><span>FIG. 0{Math.max(1, planets.findIndex((planet) => planet.id === selected) + 1)}</span> / {selectedPlanet?.name?.toUpperCase() || "EARTH"} <span className="label-rule" /></div>
          </div>

          <aside className="hero-console" aria-label="Selected world and data status">
            <div className="console-heading"><span><SatelliteDish size={14} /> WORLD SELECT</span><span>01 — 0{Math.max(1, planets.length)}</span></div>
            <div className="world-list" role="tablist" aria-label="Select a planetary body">
              {planets.map((planet, index) => (
                <button key={planet.id} role="tab" aria-selected={selected === planet.id} className={`world-option ${selected === planet.id ? "active" : ""}`} onClick={() => { setSelected(planet.id); setDatasetCategory("all"); }}>
                  <span className={`world-symbol ${planet.id}`}><i /></span>
                  <span className="world-name"><small>0{index + 1} / {planet.type || "BODY"}</small><strong>{planet.name}</strong></span>
                  {selected === planet.id && <ArrowRight className="world-arrow" size={15} />}
                </button>
              ))}
              {!loading && planets.length === 0 && <span className="console-empty">Planet catalogue unavailable</span>}
            </div>
            <div className="console-divider" />
            <div className="console-heading"><span><Activity size={14} /> SELECTED PROFILE</span><span className="console-live"><i /> LIVE</span></div>
            <p className="console-description">{selectedPlanet?.description || descriptions[selected] || "Planet data will appear when the API connects."}</p>
            <div className="console-readout"><span>DATASETS INDEXED</span><strong>{String(visibleDatasets.length).padStart(2, "0")}</strong></div>
            <div className="console-readout"><span>REFERENCE ROLE</span><strong className="readout-role">{selectedPlanet?.role || "Awaiting API"}</strong></div>
          </aside>

          <div className="hero-coordinate"><span className="coordinate-dot" /> SYSTEM COORDINATES <strong>00° 00′ 00″</strong><span className="coordinate-axis">X / Y / Z</span></div>
          <div className="hero-scroll" onClick={() => scrollTo("planet-explorer")} role="button" tabIndex={0} onKeyDown={(event) => event.key === "Enter" && scrollTo("planet-explorer")}><span>SCROLL TO EXPLORE</span><i /></div>
        </section>

        <section className="mission-strip" aria-label="Platform status">
          <div className="mission-label"><Radio size={14} /><span>MISSION TELEMETRY</span></div>
          <div className="mission-metric"><small>NETWORK</small><strong className={apiStatus === "online" ? "metric-good" : ""}>{apiStatus === "online" ? "CONNECTED" : apiStatus === "offline" ? "STANDBY" : "SYNCING"}</strong></div>
          <div className="mission-metric"><small>CELESTIAL BODIES</small><strong>{loading ? "--" : String(planets.length).padStart(2, "0")}</strong></div>
          <div className="mission-metric"><small>DATA RECORDS</small><strong>{loading ? "--" : String(datasets.length).padStart(2, "0")}</strong></div>
          <div className="mission-metric"><small>ANALYSIS MODULE</small><strong className={apiStatus === "online" ? "metric-good" : ""}>{apiStatus === "online" ? "READY" : "WAITING"}</strong></div>
          <div className="telemetry-wave" aria-hidden="true"><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /></div>
        </section>

        <section className="planet-explorer page-section" id="planet-explorer">
          <div className="section-heading">
            <div><span className="section-eyebrow">01 / THE CELESTIAL INDEX</span><h2>Three worlds.<br /><em>One reference.</em></h2></div>
            <p>Move between planetary bodies to inspect their profiles and available research data. Your selection updates the orbital view above.</p>
          </div>
          {!loading && planets.length === 0 && <ErrorNotice>The planetary catalogue could not be loaded. Confirm the backend is running.</ErrorNotice>}
          <div className="planet-cards">
            {planets.map((planet, index) => {
              const count = datasets.filter((dataset) => dataset.planet === planet.id).length;
              return <button key={planet.id} className={`planet-card ${selected === planet.id ? "selected" : ""}`} onClick={() => { setSelected(planet.id); setDatasetCategory("all"); scrollTo("dashboard"); }}>
                <div className="planet-card-top"><span>0{index + 1} / {planet.type || "BODY"}</span><ArrowDownRight size={16} /></div>
                <span className={`planet-card-orb ${planet.id}`}><i /></span>
                <div className="planet-card-copy"><h3>{planet.name}</h3><p>{descriptions[planet.id] || planet.description}</p></div>
                <div className="planet-card-bottom"><span>{String(count).padStart(2, "0")} DATASETS</span><span>EXPLORE BODY <ArrowRight size={13} /></span></div>
              </button>;
            })}
          </div>
        </section>

        <section className="data-section page-section" id="earth-analogs">
          <div className="section-heading data-heading">
            <div><span className="section-eyebrow">02 / THE RESEARCH ARCHIVE</span><h2>Surface <em>intelligence.</em></h2></div>
            <div className="archive-caption"><Database size={15} /><p>Catalogue records synchronized from the TerraTwin API.<br /><span>Showing {selectedPlanet?.name || "selected body"} datasets.</span></p></div>
          </div>
          {!loading && visibleDatasets.length > 0 && <div className="dataset-tools">
            <label className="dataset-search"><span>SEARCH RECORDS</span><input value={datasetSearch} onChange={(event) => setDatasetSearch(event.target.value)} placeholder="Dataset, instrument, source…" /></label>
            <div className="dataset-filters" aria-label="Filter datasets by category">
              <button className={datasetCategory === "all" ? "active" : ""} onClick={() => setDatasetCategory("all")}>ALL <span>{visibleDatasets.length}</span></button>
              {datasetCategories.map((category) => <button key={category} className={datasetCategory === category ? "active" : ""} onClick={() => setDatasetCategory(category)}>{category.replaceAll("_", " ")}</button>)}
            </div>
            <span className="dataset-result-count">{filteredDatasets.length} / {visibleDatasets.length} RECORDS</span>
          </div>}
          {loading ? <p className="muted-copy">Loading dataset catalogue…</p> : filteredDatasets.length ? <div className="dataset-grid">
            {filteredDatasets.map((dataset, index) => <article className="dataset-card" key={`${dataset.dataset_id}-${dataset.product_type}`}>
              <div className="dataset-card-top"><span>RECORD / {String(index + 1).padStart(2, "0")}</span><span className={`dataset-status ${dataset.catalogue_status}`}>{dataset.catalogue_status}</span></div>
              <div className="dataset-card-icon"><Database size={18} strokeWidth={1.4} /></div>
              <h3>{dataset.name}</h3><p>{dataset.purpose}</p>
              <dl><div><dt>Instrument</dt><dd>{dataset.instrument || "—"}</dd></div><div><dt>Resolution</dt><dd>{dataset.resolution || "Not specified"}</dd></div><div><dt>Provider</dt><dd>{dataset.provider}</dd></div></dl>
              {dataset.local_files?.length > 0 && <div className="dataset-local-files"><span>LOCAL DATA</span>{dataset.local_files.map((file) => <code key={file}>{file}</code>)}</div>}
              <div className="dataset-id">{dataset.dataset_id}</div>
            </article>)}
          </div> : visibleDatasets.length ? <p className="muted-copy">No datasets match these filters.</p> : <p className="muted-copy">No catalogue entries are available for this body.</p>}
        </section>

        <section className="comparison-section page-section" id="analog-comparison">
          <div className="comparison-intro"><span className="section-eyebrow">03 / THE ANALOG FINDER</span><h2>Somewhere on Earth<br />is a <em>familiar world.</em></h2><p>Compare lunar and Martian terrain with cached Earth landscapes using TerraTwin's elevation-shape method.</p><div className="comparison-note"><Crosshair size={15} /><span>PRELIMINARY TERRAIN-SHAPE ANALYSIS</span></div></div>
          <div className="comparison-workspace">
            <form className="comparison-form" onSubmit={runComparison}>
              <div className="form-heading"><span>NEW COMPARISON</span><span>INPUT / 01</span></div>
              <label>Target body<select value={targetPlanet} onChange={(event) => { setTargetPlanet(event.target.value); setLocationError(""); clearAnalysis(); }}><option value="moon">Moon</option><option value="mars">Mars</option></select></label>
              <label>Target location<select value={targetLocation} onChange={(event) => { setTargetLocation(event.target.value); clearAnalysis(); }} required><option value="" disabled>Select a supported site</option>{locations.map((location) => <option key={location.id} value={location.name}>{location.name}</option>)}</select></label>
              <ErrorNotice>{locationError || compareError}</ErrorNotice>
              <button className="primary-action" type="submit" disabled={comparing || !targetLocation.trim()}>{comparing ? "ANALYZING TERRAIN…" : <>RUN ANALYSIS <ArrowRight size={16} /></>}</button>
              <button className="clear-analysis-action" type="button" onClick={clearAnalysis} disabled={comparing}>CLEAR ANALYSIS</button>
              {analysisStarted && <div className="form-footnote"><span className="console-live"><i /> API REQUEST READY</span><span>CACHED EARTH CANDIDATES</span></div>}
            </form>
            {analysisStarted && <>
            {(earthCandidates.length > 0 || earthCandidateError) && <div className="map-action-row"><span><MapPin size={14} /> EARTH ANALOG LOCATIONS <b>{earthCandidates.length}</b></span><button type="button" onClick={() => setMapOpen((open) => !open)} aria-expanded={mapOpen} aria-controls="earth-analog-map">{mapOpen ? <><X size={14} /> HIDE MAP</> : <><MapPin size={14} /> SHOW MAP</>}</button></div>}
            {mapOpen && earthCandidateError && !earthCandidates.length && <div className="map-load-error" role="alert"><span>{earthCandidateError}</span><button type="button" onClick={retryEarthCandidates}>RETRY</button></div>}
            {mapOpen && earthCandidates.length > 0 && <Suspense fallback={<div className="map-loading">Loading Earth reference map…</div>}><AnalogMap id="earth-analog-map" candidates={earthCandidates} results={comparison?.results || []} /></Suspense>}
            {comparing ? <div className="comparison-loading" role="status"><span className="section-eyebrow">ANALYSIS IN PROGRESS</span><p>Matching {targetLocation} with the available Earth terrain records…</p></div> : comparison ? <div className="comparison-results" aria-live="polite">
              <div className="result-header"><span className="section-eyebrow">ANALYSIS COMPLETE</span><h3>{comparison.target_location}</h3><p>{comparison.target_planet} / {comparison.algorithm}</p></div>
              <div className="result-count"><strong>{String(comparison.candidate_count).padStart(2, "0")}</strong><span>EARTH REGIONS<br />RANKED</span></div>
              {bestVisualMatch && <section className="terrain-comparison-visual" aria-label="Side-by-side terrain elevation comparison">
                <div className="terrain-visual-heading"><span className="section-eyebrow">TERRAIN VISUAL COMPARISON</span><span>RANK 0{bestVisualMatch.rank} / {bestVisualMatch.similarity_score}% SHAPE MATCH</span></div>
                <div className="terrain-image-pair">
                  <figure className="terrain-image-card"><div className="terrain-image"><img src={targetTerrain.image} alt={`Elevation relief around ${comparison.target_location} on ${targetPlanet}`} loading="lazy" /><span>10 KM SAMPLE RADIUS</span></div><figcaption><small>{targetTerrain.body}</small><strong>{targetTerrain.source}</strong></figcaption></figure>
                  <div className="terrain-pair-arrow"><ArrowRight size={19} /></div>
                  <figure className="terrain-image-card"><div className="terrain-image"><img src={`/analogs/earth/${siteSlug(bestVisualMatch.location)}.png`} alt={`Elevation relief around ${bestVisualMatch.location}, an Earth terrain candidate`} loading="lazy" /><span>10 KM SAMPLE RADIUS</span></div><figcaption><small>EARTH / {bestVisualMatch.location.toUpperCase()}</small><strong>COPERNICUS GLO-30 · ~30 M / PIXEL</strong></figcaption></figure>
                </div>
                <p className="terrain-visual-note">Elevation relief from cached DEMs. Contrast is normalized per image; the outlined circles show the 10 km analysis radius. Pixel scales differ by source.</p>
              </section>}
              {comparison.results?.length ? <div className="results-list">{comparison.results.map((result) => <button type="button" aria-pressed={(bestVisualMatch?.location || "") === result.location} className={`analog-result ${(bestVisualMatch?.location || "") === result.location ? "active" : ""}`} key={`${result.rank}-${result.location}`} onClick={() => setVisualizedMatch(result.location)}><div className="result-rank">0{result.rank}</div><div className="result-name"><h4>{result.location}</h4><p>{result.region_type || "Earth analog region"} · {result.coordinates ? `${result.coordinates.latitude}°, ${result.coordinates.longitude}°` : "Coordinates unavailable"}</p><small>{result.data_quality?.source || "Terrain features"} · {result.data_quality?.selected_pixels?.toLocaleString?.() || "—"} pixels sampled</small></div><div className="similarity"><div className="similarity-track"><i style={{ width: `${result.similarity_score}%` }} /></div><strong>{result.similarity_score}<small>%</small></strong><span>SHAPE MATCH</span></div></button>)}</div> : <p className="muted-copy">No Earth candidate regions were available for this comparison.</p>}
              {comparison.results?.[0]?.warnings?.[0] && <p className="result-limitation">ⓘ {comparison.results[0].warnings[0]}</p>}
            </div> : null}
            </>}
          </div>
          {analysisStarted && <section className="terrain-atlas" aria-labelledby="terrain-atlas-title">
            <div className="terrain-atlas-heading">
              <div><span className="section-eyebrow">VISUAL REFERENCE / {targetPlanet.toUpperCase()}</span><h3 id="terrain-atlas-title">Compare the terrain side by side.</h3></div>
              <p>Choose an Earth region to load it into the analysis form. Run the comparison to see its shape score.</p>
            </div>
            <div className="atlas-target">
              <img src={targetTerrain.image} alt={`Elevation map of ${targetTerrain.body}`} loading="lazy" />
              <div><span>PLANETARY REFERENCE</span><strong>{targetTerrain.body}</strong><small>{targetTerrain.source}</small></div>
              <div className="atlas-target-note"><Crosshair size={14} /><span>Fixed 10 km sample area<br />around the selected target site</span></div>
            </div>
            <div className="terrain-atlas-grid">
              {earthCandidates.map((site) => {
                const ranked = rankedEarthSites.get(site.location);
                const selectedSite = (focusedEarthSite || comparison?.results?.[0]?.location) === site.location;
                return <button type="button" className={`atlas-site ${selectedSite ? "selected" : ""}`} key={site.location} onClick={() => { setFocusedEarthSite(site.location); if (comparison) setVisualizedMatch(site.location); }} aria-pressed={selectedSite}>
                  <div className="atlas-site-images">
                    <figure><img src={targetTerrain.image} alt={`Elevation relief map of ${targetTerrain.body}`} loading="lazy" /><figcaption>{targetTerrain.body}</figcaption></figure>
                    <ArrowRight size={16} aria-hidden="true" />
                    <figure><img src={`/analogs/earth/${siteSlug(site.location)}.png`} alt={`Elevation relief map of ${site.location}`} loading="lazy" /><figcaption>EARTH / {site.location.toUpperCase()}</figcaption></figure>
                    {ranked && <b className="atlas-rank">RANK 0{ranked.rank}</b>}
                  </div>
                  <div className="atlas-site-copy"><strong>{site.location}</strong><span>{site.region_type || "Earth terrain region"}</span><small>{site.coordinates ? `${site.coordinates.latitude.toFixed(2)}°, ${site.coordinates.longitude.toFixed(2)}°` : "Coordinates unavailable"} · {site.radius_km ?? 10} km sample</small></div>
                  <div className="atlas-site-footer"><span>{selectedSite ? "FOCUSED REFERENCE" : "FOCUS THIS REGION"}</span><strong>{ranked ? `${ranked.similarity_score}% SHAPE MATCH` : site.source || "TERRAIN DATA"}</strong></div>
                </button>;
              })}
              {!earthCandidates.length && <p className="muted-copy">Earth terrain references load from the analysis API.</p>}
            </div>
            <p className="atlas-note">These are elevation-relief maps, not surface photographs. Color and contrast are normalized for each region, so compare shapes rather than absolute colors or heights. Earth tiles use Copernicus GLO-30; lunar and Martian maps use lower-resolution global elevation products.</p>
          </section>}
        </section>
      </main>

      {assistantOpen && <aside className="assistant-panel" aria-label="TerraTwin AI research assistant">
        <div className="assistant-panel-header">
          <div className="assistant-avatar"><Bot size={18} /></div>
          <div className="assistant-title"><span>TERRATWIN / AI</span><strong>Research assistant</strong></div>
          <span className={`assistant-connection ${assistantStatus}`}><i />{assistantStatus === "online" ? "ONLINE" : assistantStatus === "checking" ? "CONNECTING" : assistantStatus === "offline" ? "OFFLINE" : "READY"}</span>
          <button className="assistant-icon-button" onClick={() => setAssistantOpen(false)} aria-label="Close assistant"><X size={17} /></button>
        </div>
        <div className="assistant-context"><Crosshair size={13} /><span>PLANETARY ANALOG DISCOVERY</span><button type="button" onClick={() => setChatMessages([])} disabled={!chatMessages.length || chatSending}>NEW CHAT</button></div>
        <div className="assistant-messages" aria-live="polite" aria-relevant="additions text">
          {!chatMessages.length && <div className="assistant-welcome">
            <span className="assistant-welcome-mark"><Sparkles size={21} /></span>
            <h2>Explore worlds<br /><em>with context.</em></h2>
            <p>Ask about lunar and Martian sites, Earth analogs, terrain scores, or the datasets in this dashboard.</p>
            <div className="assistant-prompts">
              <button type="button" onClick={() => sendAssistantMessage("Compare Jezero Crater on Mars with Earth analogs")}>Compare Jezero Crater <ArrowRight size={13} /></button>
              <button type="button" onClick={() => sendAssistantMessage("Compare Shackleton Crater on the Moon with Earth analogs")}>Find a Shackleton analog <ArrowRight size={13} /></button>
              <button type="button" onClick={() => sendAssistantMessage("What do the terrain-shape scores mean?")}>Explain terrain scores <ArrowRight size={13} /></button>
            </div>
          </div>}
          {chatMessages.map((message) => <article className={`chat-message ${message.role}`} key={message.id}>
            <span className="chat-message-label">{message.role === "assistant" ? "TERRATWIN AI" : "YOU"}</span>
            <p>{message.content}</p>
            {message.comparison?.results?.length > 0 && <div className="assistant-comparison">
              <div><span>LIVE ANALOG RANKING</span><strong>{message.comparison.target_location} / {message.comparison.target_planet}</strong></div>
              {message.comparison.results.slice(0, 3).map((result) => <div className="assistant-result" key={`${result.rank}-${result.location}`}><span><b>0{result.rank}</b>{result.location}</span><strong>{result.similarity_score}%</strong></div>)}
              {message.comparison.results[0]?.warnings?.[0] && <small>{message.comparison.results[0].warnings[0]}</small>}
            </div>}
          </article>)}
          {chatSending && <div className="assistant-thinking"><span /><span /><span /><small>Reviewing the research context</small></div>}
          {chatError && <p className="assistant-error" role="alert">{chatError}</p>}
          <div ref={chatEndRef} />
        </div>
        <form className="assistant-composer" onSubmit={sendAssistantMessage}>
          <label className="sr-only" htmlFor="assistant-prompt">Ask TerraTwin AI</label>
          <textarea id="assistant-prompt" value={chatDraft} onChange={(event) => setChatDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); sendAssistantMessage(event); } }} placeholder="Ask about a world or analog site..." rows={2} maxLength={2000} />
          <button type="submit" disabled={!chatDraft.trim() || chatSending} aria-label="Send message"><Send size={16} /></button>
          <div className="assistant-composer-note"><span>SHIFT + ENTER FOR A NEW LINE</span><span>{chatDraft.length} / 2000</span></div>
        </form>
        <div className="assistant-footnote">AI responses can be imperfect. Comparison rankings come from TerraTwin analysis data.</div>
      </aside>}

      <footer className="terra-footer"><div className="footer-brand"><Orbit size={17} /><strong>TERRATWIN</strong></div><span>EARTH / MOON / MARS ANALOG RESEARCH</span><button onClick={() => scrollTo("dashboard")}>RETURN TO ORBIT ↑</button></footer>
    </div>
  );
}
