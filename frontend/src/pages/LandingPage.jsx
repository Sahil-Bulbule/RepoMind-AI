import React, { useState } from 'react';
import GithubIcon from '../components/GithubIcon';
import {
  ArrowRight,
  ShieldCheck,
  Cpu,
  GitFork,
  FileCode,
  Loader2,
} from 'lucide-react';

const FEATURE_CARDS = [
  {
    icon: Cpu,
    title: 'Repository Intelligence',
    description: 'Deep recursive tree parsing, AST filtering, and real implementation logic extraction across your entire portfolio.',
  },
  {
    icon: ShieldCheck,
    title: 'RAG-Powered Grounding',
    description: 'Semantic chunking with isolated ChromaDB vector indexing and hybrid reranking for pinpoint-accurate responses.',
  },
  {
    icon: FileCode,
    title: 'Verifiable Citations',
    description: 'Every answer includes direct GitHub permalinks to exact source files and line ranges. Zero hallucination.',
  },
  {
    icon: GitFork,
    title: 'Multi-Project Synthesis',
    description: 'Inquire across entire developer profiles — trace architecture patterns, compare tech stacks, or drill into one repo.',
  },
];

const SAMPLE_USERNAMES = ['Sahil-Bulbule', 'pallets', 'facebook', 'torvalds'];

const STATS = [
  { value: 'ANY', label: 'GitHub Profiles' },
  { value: 'DEEP', label: 'Codebase Analysis' },
  { value: 'GROUNDED', label: 'AI Responses' },
  { value: 'MULTI', label: 'Repositories' },
];

export default function LandingPage({ onAnalyze, isLoading, error }) {
  const [usernameInput, setUsernameInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (usernameInput.trim()) onAnalyze(usernameInput.trim());
  };

  const handleSelectSample = (sample) => {
    setUsernameInput(sample);
    onAnalyze(sample);
  };

  return (
    <div className="landing-page">
      <section className="landing-hero">
        <div className="landing-hero-inner">
          <h1 className="landing-title animate-fade-up" style={{ animationDelay: '0.05s' }}>
            Ask anything about
            <br className="hidden sm:block" />{' '}
            <span>any GitHub profile</span>
          </h1>

          <p className="landing-subtitle animate-fade-up" style={{ animationDelay: '0.1s' }}>
            Explore any GitHub repository with AI-powered answers grounded in its source code.
          </p>

          <div className="landing-search-wrap animate-fade-up" style={{ animationDelay: '0.15s' }}>
            <form onSubmit={handleSubmit} className="landing-search-form">
              <div className="landing-input-wrap">
                <GithubIcon className="landing-github-icon" />
                <input
                  id="github-username-input"
                  type="text"
                  value={usernameInput}
                  onChange={(e) => setUsernameInput(e.target.value)}
                  placeholder="Enter GitHub username..."
                  className="landing-input"
                  disabled={isLoading}
                  autoComplete="off"
                  aria-label="GitHub username"
                />
              </div>

              <button
                id="analyze-btn"
                type="submit"
                disabled={!usernameInput.trim() || isLoading}
                className="landing-submit"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Indexing...</span>
                  </>
                ) : (
                  <>
                    <span>Analyze Profile</span>
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </form>

            {error && (
              <div className="landing-error" role="alert">
                {error}
              </div>
            )}

            <div className="landing-examples">
              <span className="landing-examples-label">Try an example</span>
              <div className="landing-example-list">
                {SAMPLE_USERNAMES.map((sample) => (
                  <button
                    key={sample}
                    id={`sample-${sample}`}
                    type="button"
                    onClick={() => handleSelectSample(sample)}
                    disabled={isLoading}
                    className="landing-example-chip"
                  >
                    @{sample}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="landing-stats animate-fade-up" style={{ animationDelay: '0.2s' }}>
            {STATS.map((stat) => (
              <div key={stat.label} className="landing-stat">
                <div className="landing-stat-value">{stat.value}</div>
                <div className="landing-stat-label">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="landing-content">
        <div className="landing-section-heading">
          <div className="landing-section-kicker">BUILT FOR DEVELOPERS</div>
          <h2>Built for real codebases</h2>
        </div>

        <div className="landing-feature-grid">
          {FEATURE_CARDS.map((feat) => {
            const Icon = feat.icon;
            return (
              <article key={feat.title} className="landing-feature-card">
                <div className="landing-feature-icon">
                  <Icon className="h-5 w-5" />
                </div>
                <h3>{feat.title}</h3>
                <p>{feat.description}</p>
              </article>
            );
          })}
        </div>

        <div className="landing-guarantee">
          <div className="landing-guarantee-main">
            <div className="landing-guarantee-icon">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div className="landing-guarantee-copy">
              <div className="landing-guarantee-kicker">AI-Powered Repository Insights</div>
              <h3>Ask. Explore. Understand.</h3>
              <p>Analyze your GitHub repositories and interact with them using AI-powered retrieval.</p>
            </div>
          </div>
          <div className="landing-tech-list" aria-label="Technology stack">
            {['ChromaDB', 'AI Models', 'FastAPI', 'RAG'].map((tech) => (
              <span key={tech} className="landing-tech-badge">{tech}</span>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
