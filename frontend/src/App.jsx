import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import LiveProgress from './components/LiveProgress';
import ChatInterface from './components/ChatInterface';
import SearchModal from './components/SearchModal';
import RepoCard from './components/RepoCard';
import RepoDetailModal from './components/RepoDetailModal';
import { api } from './services/api';
import { FolderGit2 } from 'lucide-react';

export default function App() {
  const [currentUsername, setCurrentUsername] = useState('');
  const [profileData, setProfileData] = useState(null);
  const [repositories, setRepositories] = useState([]);
  const [currentView, setCurrentView] = useState('landing');                                                            
  const [indexingStatus, setIndexingStatus] = useState(null);
  const [isStartingIndex, setIsStartingIndex] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [selectedRepository, setSelectedRepository] = useState(null);
  const [searchInitialQuery, setSearchInitialQuery] = useState('');
  const [selectedRepoModal, setSelectedRepoModal] = useState(null);
  
  const pollIntervalRef = useRef(null);

                            
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);


                              
  const startPollingStatus = (targetUsername) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    let loadedRepositories = false;

    const poll = async () => {
      try {
        const stat = await api.getStatus(targetUsername);
        setIndexingStatus(stat);

        if (stat.status === 'completed') {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
          await loadProfileAndRepos(targetUsername);
        } else if (stat.status === 'error') {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
          setErrorMsg(stat.error_message || 'Indexing failed.');
        } else if (!loadedRepositories && stat.progress_pct >= 35) {
          loadedRepositories = true;
          await loadProfileAndRepos(targetUsername);
        }
      } catch (err) {
        console.error('Status poll error:', err);
      }
    };

    void poll();
    pollIntervalRef.current = setInterval(poll, 500);
  };

  const loadProfileAndRepos = async (targetUsername) => {
    try {
      const [prof, repos] = await Promise.all([
        api.getProfile(targetUsername),
        api.getRepositories(targetUsername),
      ]);
      setProfileData(prof);
      setRepositories(repos || []);
      setCurrentView('dashboard');
      return { profile: prof, repositories: repos || [] };
    } catch (err) {
      console.error('Failed to load profile/repos:', err);
      setErrorMsg(err.message);
      return null;
    }
  };

                                     
  const handleAnalyze = async (username) => {
    setErrorMsg(null);
    setIsStartingIndex(true);
    setCurrentUsername(username);
    setIndexingStatus({
      username: username.toLowerCase(),
      status: 'processing',
      progress_pct: 5,
      current_step: 'Connecting to GitHub',
      step_detail: `Looking up @${username}...`,
    });
    setCurrentView('indexing');

    try {
                                            
      const existingStatus = await api.getStatus(username);
      if (existingStatus.status === 'completed') {
        const cachedProfile = await loadProfileAndRepos(username);
        if (
          cachedProfile
          && cachedProfile.repositories.length !== cachedProfile.profile.public_repos
        ) {
          setProfileData((profile) => profile ? { ...profile, status: 'indexing' } : profile);
          const refreshStatus = await api.refreshUser(username);
          setIndexingStatus(refreshStatus);
          startPollingStatus(username);
        }
        setIsStartingIndex(false);
        return;
      }

                          
      setCurrentView('indexing');
      const startRes = await api.analyzeUser(username, false);
      setIndexingStatus(startRes);
      startPollingStatus(username);
    } catch (err) {
      console.error('Analysis trigger failed:', err);
      setErrorMsg(err.message || 'Failed to start indexing.');
      setCurrentView('landing');
    } finally {
      setIsStartingIndex(false);
    }
  };

                              
  const handleRefresh = async () => {
    if (!currentUsername || isRefreshing) return;
    setIsRefreshing(true);
    setProfileData((profile) => profile ? { ...profile, status: 'indexing' } : profile);

    try {
      const refRes = await api.refreshUser(currentUsername);
      setIndexingStatus(refRes);
      startPollingStatus(currentUsername);
    } catch (err) {
      console.error('Refresh failed:', err);
      setErrorMsg(err.message);
    } finally {
      setIsRefreshing(false);
    }
  };

                     
  const handleResetProfile = () => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    setCurrentUsername('');
    setProfileData(null);
    setRepositories([]);
    setSelectedRepository(null);
    setIndexingStatus(null);
    setErrorMsg(null);
    setCurrentView('landing');
  };

                               
  const handleOpenChat = (repo = null) => {
    if (!repo) {
      setSelectedRepository(null);
    } else {
      const selected = typeof repo === 'string'
        ? repositories.find((item) =>
          item.name.toLocaleLowerCase() === repo.trim().toLocaleLowerCase()
          || item.full_name?.toLocaleLowerCase() === repo.trim().toLocaleLowerCase()
        )
        : repositories.find((item) => item.id === repo.id);
      if (!selected) {
        setErrorMsg(`Repository '${typeof repo === 'string' ? repo : repo.name}' is not in the indexed profile.`);
        return;
      }
      setSelectedRepository(selected);
    }
    setCurrentView('chat');
  };

                                   
  const handleOpenSearch = (tech) => {
    setSearchInitialQuery(tech);
    setCurrentView('search');
  };

  return (
    <div className="app-shell flex min-h-screen flex-col font-sans bg-white text-gray-900">
      
                            
      <Navbar
        currentUsername={currentUsername}
        profileData={profileData}
        currentView={currentView}
        setCurrentView={setCurrentView}
        onResetProfile={handleResetProfile}
        onRefreshProfile={handleRefresh}
        isRefreshing={isRefreshing}
      />

                               
      <main className="flex-1">
        {currentView === 'landing' && (
          <LandingPage
            onAnalyze={handleAnalyze}
            isLoading={isStartingIndex}
            error={errorMsg}
          />
        )}

        {currentView === 'indexing' && (
          <LiveProgress
            username={currentUsername}
            statusData={indexingStatus}
            onRetry={() => handleAnalyze(currentUsername)}
            onContinueToChat={() => setCurrentView('dashboard')}
          />
        )}

        {currentView === 'dashboard' && (
          <DashboardPage
            username={currentUsername}
            profileData={profileData}
            repositories={repositories}
            onRefresh={handleRefresh}
            isRefreshing={isRefreshing}
            onOpenChat={handleOpenChat}
            onOpenSearch={handleOpenSearch}
          />
        )}

        {currentView === 'chat' && (
          <div className="px-4 sm:px-6 lg:px-8">
            <ChatInterface
              key={selectedRepository ? `repo-${selectedRepository.id}` : 'global-chat'}
              username={currentUsername}
              profileData={profileData}
              repository={selectedRepository}
              onClearRepoFilter={() => setSelectedRepository(null)}
            />
          </div>
        )}

        {currentView === 'repositories' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <FolderGit2 className="w-5 h-5 text-rose-500" />
                <span>All Public Repositories for @{currentUsername}</span>
              </h2>
              <span className="text-xs font-mono text-rose-500">
                {repositories.length} repositories
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {repositories.map((repo) => (
                <RepoCard
                  key={repo.id}
                  repo={repo}
                  isIndexing={profileData?.status === 'indexing'}
                  onSelectRepo={(r) => setSelectedRepoModal(r)}
                  onAskAboutRepo={handleOpenChat}
                />
              ))}
            </div>

            {selectedRepoModal && (
              <RepoDetailModal
                username={currentUsername}
                repo={selectedRepoModal}
                onClose={() => setSelectedRepoModal(null)}
                onAskAboutRepo={handleOpenChat}
              />
            )}
          </div>
        )}

        {currentView === 'search' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <SearchModal
              username={currentUsername}
              repositories={repositories}
              initialQuery={searchInitialQuery}
              onAskAboutRepository={(repo) => handleOpenChat(repo)}
            />
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
