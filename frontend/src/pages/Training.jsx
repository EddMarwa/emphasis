import React, { useState } from 'react';
import { Play, Clock, CheckCircle2, FileText, Download, Eye } from 'lucide-react';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';

const categories = ['All', 'Getting Started', 'Deposits', 'Trading', 'Withdrawals'];

const videos = [
  { id: 1, title: 'Welcome to Quantum Capital', category: 'Getting Started', duration: '5:23', watched: true, thumbnail: '🎥' },
  { id: 2, title: 'How to Create Your Account', category: 'Getting Started', duration: '3:15', watched: true, thumbnail: '🎥' },
  { id: 3, title: 'Making Your First Deposit', category: 'Deposits', duration: '7:42', watched: false, thumbnail: '🎥' },
  { id: 4, title: 'Depositing via M-Pesa', category: 'Deposits', duration: '4:30', watched: false, thumbnail: '🎥' },
  { id: 5, title: 'Understanding the Trading Bot', category: 'Trading', duration: '12:15', watched: false, thumbnail: '🎥' },
  { id: 6, title: 'Trading Strategies Explained', category: 'Trading', duration: '15:20', watched: false, thumbnail: '🎥' },
  { id: 7, title: 'Withdrawal Process', category: 'Withdrawals', duration: '6:45', watched: false, thumbnail: '🎥' },
  { id: 8, title: 'Withdrawing via USDT', category: 'Withdrawals', duration: '5:10', watched: false, thumbnail: '🎥' },
];

const documents = [
  { id: 1, title: 'Platform Terms & Conditions', type: 'PDF', size: '2.4 MB', category: 'Getting Started' },
  { id: 2, title: 'Trading Guide - Complete Manual', type: 'PDF', size: '5.8 MB', category: 'Trading' },
  { id: 3, title: 'Security Best Practices', type: 'PDF', size: '1.2 MB', category: 'Getting Started' },
  { id: 4, title: 'Fee Structure Overview', type: 'PDF', size: '800 KB', category: 'Getting Started' },
];

const Training = ({ user, onLogout }) => {
  const [activeCategory, setActiveCategory] = useState('All');
  const [selectedVideo, setSelectedVideo] = useState(null);
  
  const filteredVideos = activeCategory === 'All' 
    ? videos 
    : videos.filter(v => v.category === activeCategory);
  
  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="space-y-8 animate-fade-in">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-dark mb-2">Training Materials</h1>
          <p className="text-text-gray">Learn how to maximize your investment potential with Quantum Capital</p>
        </div>
        
        {/* Category Tabs */}
        <div className="flex flex-wrap gap-3 bg-white p-2 rounded-xl shadow-quantum">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={`px-6 py-2 rounded-lg font-semibold transition-all duration-300 ${
                activeCategory === category
                  ? 'bg-gradient-button-primary text-white shadow-lg'
                  : 'text-text-gray hover:bg-gray-100'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
        
        {/* Video Grid */}
        <div>
          <h2 className="text-2xl font-bold text-text-dark mb-6">Video Tutorials</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVideos.map((video) => (
              <Card
                key={video.id}
                hover
                onClick={() => setSelectedVideo(video)}
                className="overflow-hidden"
              >
                <div className="relative">
                  {/* Video Thumbnail */}
                  <div className="w-full h-48 bg-gradient-primary flex items-center justify-center text-6xl">
                    {video.thumbnail}
                  </div>
                  
                  {/* Play Overlay */}
                  <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-300">
                    <div className="w-16 h-16 bg-white/90 rounded-full flex items-center justify-center">
                      <Play size={24} className="text-electric-blue ml-1" fill="currentColor" />
                    </div>
                  </div>
                  
                  {/* Watched Badge */}
                  {video.watched && (
                    <div className="absolute top-3 right-3">
                      <Badge variant="success" size="sm">
                        <CheckCircle2 size={12} className="mr-1" />
                        Watched
                      </Badge>
                    </div>
                  )}
                  
                  {/* Duration Badge */}
                  <div className="absolute bottom-3 right-3">
                    <Badge variant="neutral" size="sm" className="bg-black/70 text-white">
                      <Clock size={12} className="mr-1" />
                      {video.duration}
                    </Badge>
                  </div>
                  
                  {/* Progress Bar */}
                  {video.watched && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-emerald-500"></div>
                  )}
                </div>
                
                <div className="p-4">
                  <Badge variant="info" size="sm" className="mb-2">
                    {video.category}
                  </Badge>
                  <h3 className="font-semibold text-text-dark mb-2">{video.title}</h3>
                  {video.watched && (
                    <div className="flex items-center gap-2 text-sm text-emerald-600">
                      <CheckCircle2 size={14} />
                      <span>Completed</span>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>
        
        {/* Documents Section */}
        <div>
          <h2 className="text-2xl font-bold text-text-dark mb-6">Documents & Guides</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.map((doc) => (
              <Card key={doc.id} hover className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 bg-gradient-button-primary rounded-xl flex items-center justify-center">
                      <FileText size={24} className="text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-text-dark mb-1">{doc.title}</h3>
                      <div className="flex items-center gap-3 text-sm text-text-gray">
                        <Badge variant="neutral" size="sm">{doc.type}</Badge>
                        <span>{doc.size}</span>
                        <Badge variant="info" size="sm">{doc.category}</Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button className="p-2 text-electric-blue hover:bg-gray-100 rounded-lg transition-colors">
                      <Eye size={18} />
                    </button>
                    <button className="p-2 text-emerald-600 hover:bg-gray-100 rounded-lg transition-colors">
                      <Download size={18} />
                    </button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
        
        {/* Video Modal */}
        {selectedVideo && (
          <Modal
            isOpen={!!selectedVideo}
            onClose={() => setSelectedVideo(null)}
            title={selectedVideo.title}
            size="xl"
          >
            <div className="space-y-4">
              {/* Video Player Placeholder */}
              <div className="w-full h-96 bg-gradient-primary rounded-xl flex items-center justify-center">
                <div className="text-center text-white">
                  <Play size={64} className="mx-auto mb-4" fill="currentColor" />
                  <p className="text-xl font-semibold">Video Player</p>
                  <p className="text-sm opacity-75 mt-2">Duration: {selectedVideo.duration}</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <Badge variant="info">{selectedVideo.category}</Badge>
                <div className="flex gap-2">
                  {!selectedVideo.watched && (
                    <button className="px-4 py-2 bg-emerald-500 text-white rounded-lg font-medium hover:bg-emerald-600 transition-colors">
                      Mark as Complete
                    </button>
                  )}
                </div>
              </div>
              
              <p className="text-text-gray">
                This is a comprehensive tutorial covering all aspects of {selectedVideo.title.toLowerCase()}. 
                Follow along step by step to master this feature.
              </p>
            </div>
          </Modal>
        )}
      </div>
    </Layout>
  );
};

export default Training;

