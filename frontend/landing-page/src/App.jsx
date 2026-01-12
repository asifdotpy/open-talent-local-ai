import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Features from './pages/Features';
import Pricing from './pages/Pricing';
import Community from './pages/Community';
import Blog from './pages/Blog';
import FAQ from './pages/FAQ';
import LegalPages from './components/LegalPages';
import Download from './pages/Download';

function App() {
    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/features" element={<Features />} />
                    <Route path="/pricing" element={<Pricing />} />
                    <Route path="/community" element={<Community />} />
                    <Route path="/blog" element={<Blog />} />
                    <Route path="/faq" element={<FAQ />} />
                    <Route path="/legal" element={<LegalPages />} />
                    <Route path="/download" element={<Download />} />
                </Routes>
            </Layout>
        </Router>
    );
}

export default App;
