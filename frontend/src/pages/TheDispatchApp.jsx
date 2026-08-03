import React, { useState, useEffect, useMemo } from "react";
import {
  Search, Settings2, ArrowLeft, X, Plus, Check,
  TrendingUp, Landmark, Cpu, Trophy, Palette, FlaskConical,
  Globe2, DollarSign, Newspaper, Swords, Leaf, Rocket,
  Wifi, BatteryFull, SignalHigh, Clock, ChevronRight, Eye, EyeOff
} from "lucide-react";
import { AuthProvider, useAuth } from "../context/AuthContext.jsx";
import { signup as apiSignup, login as apiLogin, saveInterests, fetchNews, getSummary, getUserInterests } from "../api/client.js";
import { parseSummary } from "../utils/parseSummary.js";

/* ---------------------------------------------------------
   TOKENS
   bg:        #EAE0C8  parchment
   card:      #F6F1E4  warm cream
   ink:       #3E2E22  espresso (primary text)
   soft:      #8A7256  taupe (secondary text)
   line:      #C9B896  hairline / borders
   burgundy:  #6E2A2A  primary accent (CTAs, selected states)
   brass:     #A9822E  secondary accent (icons, flourishes)
   olive:     #5C6B4B  tertiary accent (unused sparingly)
--------------------------------------------------------- */

const INTEREST_DEFS = [
  { id: "indian-politics", label: "Indian Politics", icon: Landmark },
  { id: "us-politics", label: "US Politics", icon: Landmark },
  { id: "russia-sanctions", label: "Russia–US Sanctions", icon: Swords },
  { id: "world-affairs", label: "World Affairs", icon: Globe2 },
  { id: "markets", label: "Markets & Finance", icon: DollarSign },
  { id: "technology", label: "Technology", icon: Cpu },
  { id: "startups", label: "Startups", icon: Rocket },
  { id: "cricket", label: "Cricket", icon: Trophy },
  { id: "sports", label: "Sports", icon: Trophy },
  { id: "climate", label: "Climate", icon: Leaf },
  { id: "culture", label: "Culture & Arts", icon: Palette },
  { id: "science", label: "Science", icon: FlaskConical },
];

const DEFAULT_SIGNIN_IDS = ["indian-politics", "technology", "markets", "cricket", "russia-sanctions"];

const useFonts = () => {
  useEffect(() => {
    const id = "dispatch-fonts";
    if (document.getElementById(id)) return;
    const link = document.createElement("link");
    link.id = id;
    link.rel = "stylesheet";
    link.href =
      "https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&display=swap";
    document.head.appendChild(link);
  }, []);
};

function slugify(text) {
  return text.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

function StatusBar() {
  return (
    <div className="db-statusbar">
      <span className="db-statustime">9:41</span>
      <div className="db-statusicons">
        <SignalHigh size={13} strokeWidth={2.4} />
        <Wifi size={13} strokeWidth={2.4} />
        <BatteryFull size={15} strokeWidth={2.2} />
      </div>
    </div>
  );
}

function Masthead({ small }) {
  return (
    <div className={small ? "db-masthead db-masthead-sm" : "db-masthead"}>
      <div className="db-seal">D</div>
      <div>
        <div className="db-wordmark">THE DISPATCH</div>
        {!small && <div className="db-tagline">Curated intelligence, delivered daily</div>}
      </div>
    </div>
  );
}

function Chip({ label, Icon, active, onClick, onRemove }) {
  return (
    <button className={"db-chip" + (active ? " db-chip-active" : "")} onClick={onClick}>
      {Icon && <Icon size={14} strokeWidth={2} />}
      <span>{label}</span>
      {active && onRemove && (
        <X
          size={13}
          strokeWidth={2.5}
          className="db-chip-x"
          onClick={(e) => { e.stopPropagation(); onRemove(); }}
        />
      )}
    </button>
  );
}

function DispatchAppInner() {
  useFonts();
  const { token, isAuthenticated, login: setAuthToken, logout } = useAuth();

  const [screen, setScreen] = useState("login");
  const [authMode, setAuthMode] = useState("signin");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [customInterests, setCustomInterests] = useState([]);
  const [selected, setSelected] = useState([]);
  const [query, setQuery] = useState("");
  const [activeArticle, setActiveArticle] = useState(null);
  const [feedArticles, setFeedArticles] = useState([]);
  const [topicImages, setTopicImages] = useState({}); // lowercase label -> image_url from backend

  const allInterests = useMemo(
    () => [...INTEREST_DEFS, ...customInterests],
    [customInterests]
  );

  const filteredInterests = useMemo(() => {
    if (!query.trim()) return allInterests;
    return allInterests.filter((i) =>
      i.label.toLowerCase().includes(query.trim().toLowerCase())
    );
  }, [allInterests, query]);

  const showAddCustom =
    query.trim().length > 1 &&
    !allInterests.some((i) => i.label.toLowerCase() === query.trim().toLowerCase());

  const toggleInterest = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const addCustomInterest = () => {
    const label = query.trim();
    if (!label) return;
    const id = "custom-" + slugify(label);
    if (!allInterests.some((i) => i.id === id)) {
      setCustomInterests((prev) => [...prev, { id, label, icon: Newspaper }]);
    }
    setSelected((prev) => (prev.includes(id) ? prev : [...prev, id]));
    setQuery("");
  };

  const interestLabel = (id) => allInterests.find((i) => i.id === id)?.label ?? "";

  const interestIdForTopic = (topic) =>
    allInterests.find((i) => i.label.trim().toLowerCase() === topic.trim().toLowerCase())?.id ?? null;

  // Given a label coming back from the backend, find its existing chip id
  // (built-in or already-known custom), or register a new custom chip for
  // it so it shows up correctly in the onboarding/editPrefs grids too.
  const idForLabel = (label) => {
    const existing = allInterests.find(
      (i) => i.label.trim().toLowerCase() === label.trim().toLowerCase()
    );
    if (existing) return existing.id;
    const id = "custom-" + slugify(label);
    setCustomInterests((prev) =>
      prev.some((i) => i.id === id) ? prev : [...prev, { id, label, icon: Newspaper }]
    );
    return id;
  };

  // Pulls the user's previously saved interests + their images from the
  // backend. Returns the list of chip ids (registering any custom ones)
  // and merges the images into topicImages.
  const restoreSavedInterests = async (authToken) => {
    const data = await getUserInterests(authToken);
    const saved = data?.interests || [];

    const images = {};
    saved.forEach((entry) => {
      if (entry.image_url) images[entry.name.trim().toLowerCase()] = entry.image_url;
    });
    if (Object.keys(images).length) {
      setTopicImages((prev) => ({ ...prev, ...images }));
    }

    return saved.map((entry) => idForLabel(entry.name));
  };

  // Pulls news + a summary for whatever is in `selected` and builds feed cards.
  const loadFeedForSelected = async (authToken, ids) => {
    const labels = ids.map(interestLabel).filter(Boolean);
    if (labels.length === 0 || !authToken) return;

    await saveInterests(authToken, labels);

    // Refresh the image map — this also picks up Wikipedia images for
    // any brand-new custom topics that just got created server-side.
    try {
      const data = await getUserInterests(authToken);
      const images = {};
      (data?.interests || []).forEach((entry) => {
        if (entry.image_url) images[entry.name.trim().toLowerCase()] = entry.image_url;
      });
      if (Object.keys(images).length) {
        setTopicImages((prev) => ({ ...prev, ...images }));
      }
    } catch {
      // Non-fatal — feed will just fall back to placeholder images.
    }

    await fetchNews(authToken);
    const summaryResult = await getSummary(authToken);
    const sections = parseSummary(summaryResult?.summary || "");

    const cards = sections.map((section, idx) => ({
      id: idx,
      interestId: interestIdForTopic(section.topic),
      topic: section.topic,
      source: "AI Dispatch",
      time: "Just now",
      seed: slugify(section.topic) || "dispatch",
      bullets: section.bullets,
      paragraphs: section.paragraphs,
    }));
    setFeedArticles(cards);
  };

  const imageForTopic = (topic) =>
    topicImages[topic.trim().toLowerCase()] || null;

  const submitAuth = async () => {
    setErrorMsg("");

    if (authMode === "signup") {
      if (!username.trim() || !email.trim() || !password) {
        setErrorMsg("All fields are required.");
        return;
      }
      setBusy(true);
      try {
        await apiSignup({ username: username.trim(), email: email.trim(), password });
        // Log in immediately with the same credentials so the flow moves
        // straight to onboarding, same as the original design.
        const loginData = await apiLogin({ email: email.trim(), password });
        setAuthToken(loginData.access_token);
        setScreen("onboarding");
      } catch (err) {
        setErrorMsg(err.message);
      } finally {
        setBusy(false);
      }
      return;
    }

    // signin
    if (!email.trim() || !password) {
      setErrorMsg("Email and password are required.");
      return;
    }
    setBusy(true);
    try {
      const data = await apiLogin({ email: email.trim(), password });
      setAuthToken(data.access_token);

      let ids = await restoreSavedInterests(data.access_token);
      if (ids.length === 0) ids = DEFAULT_SIGNIN_IDS;

      setSelected(ids);
      await loadFeedForSelected(data.access_token, ids);
      setScreen("feed");
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setBusy(false);
    }
  };

  const confirmOnboarding = async () => {
    if (selected.length === 0) return;
    setErrorMsg("");
    setBusy(true);
    try {
      await loadFeedForSelected(token, selected);
      setScreen("feed");
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setBusy(false);
    }
  };

  const savePrefs = async () => {
    setErrorMsg("");
    setBusy(true);
    try {
      await loadFeedForSelected(token, selected);
      setScreen("feed");
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setBusy(false);
    }
  };

  const openArticle = (article) => {
    setActiveArticle(article);
    setScreen("article");
  };

  return (
    <div className="db-stage">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&display=swap');

        .db-stage {
          min-height: 100vh;
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: radial-gradient(circle at 50% 0%, #dccfae 0%, #cabb90 100%);
          padding: 40px 16px;
          font-family: 'Inter', sans-serif;
        }
        .db-phone {
          width: 380px;
          height: 780px;
          background: #EAE0C8;
          border-radius: 40px;
          border: 10px solid #2b2016;
          box-shadow: 0 30px 60px -20px rgba(30,20,10,0.5), 0 0 0 1px rgba(0,0,0,0.05);
          overflow: hidden;
          position: relative;
          display: flex;
          flex-direction: column;
        }
        .db-statusbar {
          height: 30px;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 24px;
          color: #3E2E22;
          background: #EAE0C8;
        }
        .db-statustime { font-family: 'Inter', sans-serif; font-weight: 600; font-size: 13px; letter-spacing: 0.02em; }
        .db-statusicons { display: flex; gap: 6px; align-items: center; color: #3E2E22; }
        .db-screen {
          flex: 1;
          overflow-y: auto;
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        .db-screen::-webkit-scrollbar { display: none; }
        .db-home-indicator {
          position: absolute;
          bottom: 8px;
          left: 50%;
          transform: translateX(-50%);
          width: 120px;
          height: 4px;
          border-radius: 4px;
          background: #3E2E22;
          opacity: 0.55;
        }

        .db-masthead { display: flex; align-items: center; gap: 12px; padding: 18px 20px 14px; }
        .db-masthead-sm { padding: 14px 20px 12px; }
        .db-seal {
          width: 38px; height: 38px; border-radius: 50%;
          border: 1.5px solid #A9822E;
          display: flex; align-items: center; justify-content: center;
          font-family: 'Fraunces', serif; font-weight: 600; font-size: 17px;
          color: #6E2A2A; background: #F6F1E4; flex-shrink: 0;
        }
        .db-wordmark { font-family: 'Fraunces', serif; font-weight: 600; font-size: 19px; letter-spacing: 0.06em; color: #3E2E22; }
        .db-tagline { font-family: 'Fraunces', serif; font-style: italic; font-size: 12px; color: #8A7256; margin-top: 1px; }
        .db-rule { height: 1px; background: linear-gradient(to right, transparent, #C9B896 15%, #C9B896 85%, transparent); margin: 0 20px; }
        .db-rule-double { border-top: 1px solid #C9B896; border-bottom: 1px solid #C9B896; height: 3px; margin: 0 20px 4px; }

        /* ---- Login / Signup ---- */
        .db-auth { padding: 34px 26px 26px; display: flex; flex-direction: column; align-items: center; height: 100%; box-sizing: border-box; }
        .db-auth-seal { width: 64px; height: 64px; border-radius: 50%; border: 1.5px solid #A9822E; display: flex; align-items: center; justify-content: center; font-family: 'Fraunces', serif; font-weight: 600; font-size: 28px; color: #6E2A2A; background: #F6F1E4; margin-bottom: 16px; }
        .db-auth-word { font-family: 'Fraunces', serif; font-weight: 600; font-size: 26px; letter-spacing: 0.07em; color: #3E2E22; }
        .db-auth-tag { font-family: 'Fraunces', serif; font-style: italic; font-size: 13px; color: #8A7256; margin-top: 4px; margin-bottom: 30px; }
        .db-tabswitch { display: flex; width: 100%; border: 1px solid #C9B896; border-radius: 6px; overflow: hidden; margin-bottom: 26px; }
        .db-tabswitch button { flex: 1; padding: 10px 0; font-family: 'Inter', sans-serif; font-weight: 500; font-size: 13px; letter-spacing: 0.02em; background: transparent; border: none; color: #8A7256; cursor: pointer; }
        .db-tabswitch button.active { background: #3E2E22; color: #F6F1E4; }
        .db-field { width: 100%; margin-bottom: 18px; }
        .db-field label { display: block; font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #8A7256; margin-bottom: 6px; }
        .db-field-input { display: flex; align-items: center; border-bottom: 1.5px solid #C9B896; padding-bottom: 7px; }
        .db-field-input input { flex: 1; border: none; background: transparent; outline: none; font-family: 'Source Serif 4', serif; font-size: 15px; color: #3E2E22; }
        .db-field-input input::placeholder { color: #b8a98a; }
        .db-eye { color: #8A7256; cursor: pointer; }
        .db-cta { width: 100%; padding: 13px 0; background: #6E2A2A; color: #F6EFE2; border: none; border-radius: 5px; font-family: 'Inter', sans-serif; font-weight: 600; font-size: 14px; letter-spacing: 0.03em; cursor: pointer; margin-top: 8px; box-shadow: 0 6px 14px -6px rgba(110,42,42,0.55); }
        .db-cta:active { transform: translateY(1px); }
        .db-cta:disabled { opacity: 0.5; cursor: not-allowed; }
        .db-switchline { margin-top: 18px; font-family: 'Inter', sans-serif; font-size: 12.5px; color: #8A7256; }
        .db-switchline span { color: #6E2A2A; font-weight: 600; cursor: pointer; }
        .db-error { width: 100%; font-family: 'Inter', sans-serif; font-size: 12.5px; color: #6E2A2A; background: rgba(110,42,42,0.08); border: 1px solid rgba(110,42,42,0.25); border-radius: 6px; padding: 9px 12px; margin-bottom: 16px; }

        /* ---- Onboarding / Edit prefs ---- */
        .db-onboard { padding: 22px 20px 90px; box-sizing: border-box; }
        .db-onboard-title { font-family: 'Fraunces', serif; font-weight: 600; font-size: 22px; color: #3E2E22; margin: 4px 0 6px; }
        .db-onboard-sub { font-family: 'Source Serif 4', serif; font-size: 13.5px; color: #8A7256; margin-bottom: 20px; line-height: 1.5; }
        .db-search { display: flex; align-items: center; gap: 8px; background: #F6F1E4; border: 1px solid #C9B896; border-radius: 7px; padding: 10px 12px; margin-bottom: 18px; }
        .db-search input { flex: 1; border: none; background: transparent; outline: none; font-family: 'Inter', sans-serif; font-size: 13.5px; color: #3E2E22; }
        .db-search input::placeholder { color: #a99a7c; }
        .db-search-icon { color: #8A7256; }
        .db-addcustom { display: flex; align-items: center; justify-content: space-between; background: #F6F1E4; border: 1px dashed #A9822E; border-radius: 7px; padding: 10px 12px; margin-bottom: 16px; cursor: pointer; }
        .db-addcustom span { font-family: 'Inter', sans-serif; font-size: 13px; color: #6E2A2A; }
        .db-chipgrid { display: flex; flex-wrap: wrap; gap: 9px; }
        .db-chip { display: flex; align-items: center; gap: 6px; padding: 9px 13px; border-radius: 20px; border: 1px solid #C9B896; background: #F6F1E4; font-family: 'Inter', sans-serif; font-size: 12.5px; font-weight: 500; color: #5c4b36; cursor: pointer; transition: all 0.15s ease; }
        .db-chip-active { background: #3E2E22; border-color: #3E2E22; color: #F1E7D3; }
        .db-chip-x { margin-left: 2px; }
        .db-onboard-footer { position: sticky; bottom: 0; padding: 14px 20px 18px; background: linear-gradient(to top, #EAE0C8 65%, transparent); }
        .db-footer-count { font-family: 'Inter', sans-serif; font-size: 11.5px; color: #8A7256; text-align: center; margin-bottom: 10px; }

        /* ---- Feed ---- */
        .db-feedtop { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px 10px; }
        .db-settingsbtn { width: 34px; height: 34px; border-radius: 50%; background: #F6F1E4; border: 1px solid #C9B896; display: flex; align-items: center; justify-content: center; color: #6E2A2A; cursor: pointer; }
        .db-feedlist { padding: 4px 16px 24px; display: flex; flex-direction: column; gap: 16px; }
        .db-card { background: #F6F1E4; border: 1px solid #C9B896; border-radius: 10px; overflow: hidden; cursor: pointer; box-shadow: 0 4px 10px -6px rgba(62,46,34,0.25); }
        .db-card img { width: 100%; height: 140px; object-fit: cover; display: block; border-bottom: 1px solid #C9B896; }
        .db-card-body { padding: 13px 15px 15px; }
        .db-eyebrow { font-family: 'Inter', sans-serif; font-weight: 600; font-size: 10.5px; letter-spacing: 0.09em; text-transform: uppercase; color: #6E2A2A; margin-bottom: 6px; }
        .db-headline { font-family: 'Fraunces', serif; font-weight: 600; font-size: 16.5px; line-height: 1.28; color: #3E2E22; margin-bottom: 9px; }
        .db-meta { display: flex; align-items: center; gap: 6px; font-family: 'Inter', sans-serif; font-size: 11.5px; color: #8A7256; }
        .db-emptystate { padding: 60px 30px; text-align: center; }
        .db-emptystate p { font-family: 'Source Serif 4', serif; font-size: 14px; color: #8A7256; line-height: 1.6; }

        /* ---- Article ---- */
        .db-articlehero { position: relative; }
        .db-articlehero img { width: 100%; height: 210px; object-fit: cover; display: block; }
        .db-backbtn { position: absolute; top: 14px; left: 14px; width: 34px; height: 34px; border-radius: 50%; background: rgba(246,241,228,0.92); border: 1px solid #C9B896; display: flex; align-items: center; justify-content: center; color: #3E2E22; cursor: pointer; }
        .db-articlebody { padding: 20px 22px 40px; }
        .db-articleheadline { font-family: 'Fraunces', serif; font-weight: 600; font-size: 22px; line-height: 1.32; color: #3E2E22; margin: 12px 0 10px; }
        .db-articlesummary { font-family: 'Source Serif 4', serif; font-size: 15px; line-height: 1.75; color: #4a3a2b; }
        .db-articlesummary ul { margin: 0; padding-left: 20px; }
        .db-articlesummary li { margin-bottom: 10px; }
        .db-articlesummary-label { font-family: 'Inter', sans-serif; font-weight: 600; font-size: 10.5px; letter-spacing: 0.09em; text-transform: uppercase; color: #A9822E; margin: 22px 0 8px; }
      `}</style>

      <div className="db-phone">
        <StatusBar />
        <div className="db-screen">
          {screen === "login" && (
            <div className="db-auth">
              <div className="db-auth-seal">D</div>
              <div className="db-auth-word">THE DISPATCH</div>
              <div className="db-auth-tag">Curated intelligence, delivered daily</div>

              <div className="db-tabswitch">
                <button
                  className={authMode === "signin" ? "active" : ""}
                  onClick={() => { setAuthMode("signin"); setErrorMsg(""); }}
                >
                  Sign In
                </button>
                <button
                  className={authMode === "signup" ? "active" : ""}
                  onClick={() => { setAuthMode("signup"); setErrorMsg(""); }}
                >
                  Create Account
                </button>
              </div>

              {errorMsg && <div className="db-error">{errorMsg}</div>}

              {authMode === "signup" && (
                <div className="db-field">
                  <label>Username</label>
                  <div className="db-field-input">
                    <input
                      placeholder="e.g. eleanor.hart"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                    />
                  </div>
                </div>
              )}

              <div className="db-field">
                <label>Email</label>
                <div className="db-field-input">
                  <input
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              <div className="db-field">
                <label>Password</label>
                <div className="db-field-input">
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && submitAuth()}
                  />
                  <span className="db-eye" onClick={() => setShowPassword((s) => !s)}>
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </span>
                </div>
              </div>

              <button className="db-cta" onClick={submitAuth} disabled={busy}>
                {busy ? "Please wait…" : authMode === "signup" ? "Continue" : "Enter The Dispatch"}
              </button>

              <div className="db-switchline">
                {authMode === "signup" ? (
                  <>Already a member? <span onClick={() => setAuthMode("signin")}>Sign in</span></>
                ) : (
                  <>New here? <span onClick={() => setAuthMode("signup")}>Create an account</span></>
                )}
              </div>
            </div>
          )}

          {screen === "onboarding" && (
            <div className="db-onboard">
              <Masthead small />
              <div className="db-rule" />
              <div className="db-onboard-title" style={{ marginTop: 18 }}>Choose your desk</div>
              <div className="db-onboard-sub">
                Select the beats you'd like on your front page. Search to find a topic, or add one of your own.
              </div>

              {errorMsg && <div className="db-error">{errorMsg}</div>}

              <div className="db-search">
                <Search size={15} className="db-search-icon" />
                <input
                  placeholder="Search a topic, e.g. Semiconductors"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && showAddCustom && addCustomInterest()}
                />
              </div>

              {showAddCustom && (
                <div className="db-addcustom" onClick={addCustomInterest}>
                  <span>Add "{query.trim()}" as a topic</span>
                  <Plus size={15} color="#6E2A2A" />
                </div>
              )}

              <div className="db-chipgrid">
                {filteredInterests.map((i) => (
                  <Chip
                    key={i.id}
                    label={i.label}
                    Icon={i.icon}
                    active={selected.includes(i.id)}
                    onClick={() => toggleInterest(i.id)}
                  />
                ))}
              </div>

              <div className="db-onboard-footer">
                <div className="db-footer-count">
                  {selected.length} topic{selected.length !== 1 ? "s" : ""} selected
                </div>
                <button
                  className="db-cta"
                  disabled={selected.length === 0 || busy}
                  style={selected.length === 0 ? { opacity: 0.45 } : {}}
                  onClick={confirmOnboarding}
                >
                  {busy ? "Please wait…" : "Continue to Front Page"}
                </button>
              </div>
            </div>
          )}

          {screen === "editPrefs" && (
            <div className="db-onboard">
              <div className="db-feedtop" style={{ padding: "16px 0 6px" }}>
                <div
                  className="db-settingsbtn"
                  onClick={() => setScreen("feed")}
                  style={{ borderRadius: "50%" }}
                >
                  <ArrowLeft size={16} />
                </div>
                <div className="db-onboard-title" style={{ margin: 0, fontSize: 18 }}>Edit Preferences</div>
                <div style={{ width: 34 }} />
              </div>
              <div className="db-onboard-sub" style={{ marginTop: 10 }}>
                Add or remove the beats you follow. Changes apply to your front page instantly.
              </div>

              {errorMsg && <div className="db-error">{errorMsg}</div>}

              <div className="db-search">
                <Search size={15} className="db-search-icon" />
                <input
                  placeholder="Search or add a topic"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && showAddCustom && addCustomInterest()}
                />
              </div>

              {showAddCustom && (
                <div className="db-addcustom" onClick={addCustomInterest}>
                  <span>Add "{query.trim()}" as a topic</span>
                  <Plus size={15} color="#6E2A2A" />
                </div>
              )}

              <div className="db-chipgrid">
                {filteredInterests.map((i) => (
                  <Chip
                    key={i.id}
                    label={i.label}
                    Icon={i.icon}
                    active={selected.includes(i.id)}
                    onClick={() => toggleInterest(i.id)}
                    onRemove={() => toggleInterest(i.id)}
                  />
                ))}
              </div>

              <div className="db-onboard-footer">
                <div className="db-footer-count">
                  {selected.length} topic{selected.length !== 1 ? "s" : ""} selected
                </div>
                <button className="db-cta" onClick={savePrefs} disabled={busy}>
                  {busy ? "Please wait…" : "Save Preferences"}
                </button>
              </div>
            </div>
          )}

          {screen === "feed" && (
            <div>
              <div className="db-feedtop">
                <Masthead small />
                <div className="db-settingsbtn" onClick={() => setScreen("editPrefs")}>
                  <Settings2 size={16} />
                </div>
              </div>
              <div className="db-rule-double" />

              {errorMsg && <div className="db-error" style={{ margin: "0 20px 14px" }}>{errorMsg}</div>}

              {feedArticles.length === 0 ? (
                <div className="db-emptystate">
                  <p>
                    Your front page is empty. Tap the settings icon above to choose a few topics
                    and we'll start filling it in.
                  </p>
                </div>
              ) : (
                <div className="db-feedlist">
                  {feedArticles.map((a) => (
                    <div className="db-card" key={a.id} onClick={() => openArticle(a)}>
                      <img src={imageForTopic(a.topic)} alt="" />
                      <div className="db-card-body">
                        <div className="db-eyebrow">AI Dispatch</div>
                        <div className="db-headline">{a.topic}</div>
                        <div className="db-meta">
                          <span>{a.source}</span>
                          <span>·</span>
                          <Clock size={11} />
                          <span>{a.time}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {screen === "article" && activeArticle && (
            <div>
              <div className="db-articlehero">
                <img src={imageForTopic(activeArticle.topic)} alt="" />
                <div className="db-backbtn" onClick={() => setScreen("feed")}>
                  <ArrowLeft size={16} />
                </div>
              </div>
              <div className="db-articlebody">
                <div className="db-eyebrow">AI Dispatch</div>
                <div className="db-articleheadline">{activeArticle.topic}</div>
                <div className="db-meta">
                  <span>{activeArticle.source}</span>
                  <span>·</span>
                  <Clock size={11} />
                  <span>{activeArticle.time}</span>
                </div>
                <div className="db-articlesummary-label">Summary</div>
                <div className="db-articlesummary">
                  {activeArticle.bullets && activeArticle.bullets.length > 0 && (
                    <ul>
                      {activeArticle.bullets.map((b, i) => <li key={i}>{b}</li>)}
                    </ul>
                  )}
                  {activeArticle.paragraphs && activeArticle.paragraphs.map((p, i) => (
                    <p key={i}>{p}</p>
                  ))}
                  {(!activeArticle.bullets || activeArticle.bullets.length === 0) &&
                   (!activeArticle.paragraphs || activeArticle.paragraphs.length === 0) && (
                    <p>No detail was returned for this topic.</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="db-home-indicator" />
      </div>
    </div>
  );
}

export default function TheDispatchApp() {
  return (
    <AuthProvider>
      <DispatchAppInner />
    </AuthProvider>
  );
}