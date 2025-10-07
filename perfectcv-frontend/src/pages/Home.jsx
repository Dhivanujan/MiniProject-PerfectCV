import React from "react";
import About from "../components/About";
import Contact from "../components/Contact";
import CTA from "../components/CTA";
import Footer from "../components/Footer";
import Hero from "../components/Hero";
import Navbar from "../components/Navbar";
import HowItWorks from "../components/HowItWorks";
import FAQ from "../components/FAQ";
import Testimonials from "../components/Testimonials";

function Home() {
  return (
    <div className="dark:bg-black">
      <Hero />
      <About />
      <HowItWorks/>
      <Testimonials/>
      <Contact />
      <FAQ/>
      <CTA />
      <Footer />
    </div>
  );
}

export default Home;
