import { useEffect } from "react";
import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import LandingScrollShowcase from "./components/LandingScrollShowcase";
import FeaturesSection from "./components/FeaturesSection";
import { api } from "./api/client.js";

function App() {
  useEffect(() => {
    api.health().then((r) => console.log("Backend:", r.message)).catch(() => console.warn("Backend not reachable"));
  }, []);

  return (
    <div>
      <Navbar />
      <HeroSection />
      <LandingScrollShowcase />
      <FeaturesSection />
    </div>
  );
}

export default App;
