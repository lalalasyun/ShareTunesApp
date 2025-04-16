'use client';

import { useState } from 'react';
import Image from 'next/image';

interface Track {
  id: string;
  spotify_id: string;
  name: string;
  artist: string;
  album: string;
  image_url: string;
  preview_url: string | null;
  explanation: string;
}

interface Recommendation {
  id: string;
  context_description: string | null;
  created_at: string;
  tracks: Track[];
}

interface RecommendationListProps {
  recommendations: Recommendation[];
}

export default function RecommendationList({ recommendations }: RecommendationListProps) {
  const [expandedRecommendation, setExpandedRecommendation] = useState<string | null>(null);
  const [expandedTrack, setExpandedTrack] = useState<string | null>(null);
  const [audioPlaying, setAudioPlaying] = useState<string | null>(null);
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric'
    }).format(date);
  };
  
  const handlePlayPreview = (trackId: string, previewUrl: string | null) => {
    if (!previewUrl) return;
    
    if (audioPlaying) {
      const currentAudio = document.getElementById(`audio-${audioPlaying}`) as HTMLAudioElement;
      currentAudio?.pause();
      
      if (audioPlaying === trackId) {
        setAudioPlaying(null);
        return;
      }
    }
    
    const audio = document.getElementById(`audio-${trackId}`) as HTMLAudioElement;
    audio.play();
    setAudioPlaying(trackId);
  };
  
  const handleAudioEnded = () => {
    setAudioPlaying(null);
  };
  
  const openSpotify = (spotifyId: string) => {
    window.open(`https://open.spotify.com/track/${spotifyId}`, '_blank');
  };

  return (
    <div className="space-y-6">
      {recommendations.map((recommendation) => (
        <div key={recommendation.id} className="bg-white rounded-lg shadow overflow-hidden">
          <div
            className="p-4 cursor-pointer flex justify-between items-center"
            onClick={() => setExpandedRecommendation(
              expandedRecommendation === recommendation.id ? null : recommendation.id
            )}
          >
            <div>
              <h3 className="font-semibold">
                {recommendation.context_description 
                  ? `「${recommendation.context_description}」の推薦` 
                  : '楽曲推薦'}
              </h3>
              <p className="text-sm text-gray-500">{formatDate(recommendation.created_at)}</p>
            </div>
            <svg
              className={`w-5 h-5 transition-transform ${
                expandedRecommendation === recommendation.id ? 'transform rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
          
          {expandedRecommendation === recommendation.id && (
            <div className="border-t">
              {recommendation.tracks.map((track) => (
                <div key={track.id} className="border-b last:border-b-0">
                  <div className="p-4 flex items-center">
                    <div className="relative h-16 w-16 flex-shrink-0">
                      {track.image_url ? (
                        <Image
                          src={track.image_url}
                          alt={track.album || 'アルバムアートワーク'}
                          fill
                          className="object-cover rounded"
                        />
                      ) : (
                        <div className="bg-gray-200 h-full w-full rounded flex items-center justify-center">
                          <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"></path>
                          </svg>
                        </div>
                      )}
                    </div>
                    
                    <div className="ml-4 flex-1">
                      <h4 className="font-medium">{track.name}</h4>
                      <p className="text-sm text-gray-600">{track.artist}</p>
                      {track.album && <p className="text-xs text-gray-500">{track.album}</p>}
                    </div>
                    
                    <div className="flex space-x-2">
                      {track.preview_url && (
                        <button
                          onClick={() => handlePlayPreview(track.id, track.preview_url)}
                          className="p-2 rounded-full bg-gray-100 hover:bg-gray-200"
                        >
                          {audioPlaying === track.id ? (
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd"></path>
                            </svg>
                          ) : (
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd"></path>
                            </svg>
                          )}
                          <audio
                            id={`audio-${track.id}`}
                            src={track.preview_url || ''}
                            onEnded={handleAudioEnded}
                            className="hidden"
                          />
                        </button>
                      )}
                      
                      <button
                        onClick={() => openSpotify(track.spotify_id)}
                        className="p-2 rounded-full bg-spotify-green text-white hover:bg-green-600"
                      >
                        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.48.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"></path>
                        </svg>
                      </button>
                      
                      <button
                        onClick={() => setExpandedTrack(
                          expandedTrack === track.id ? null : track.id
                        )}
                        className="p-2 rounded-full bg-gray-100 hover:bg-gray-200"
                      >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"></path>
                        </svg>
                      </button>
                    </div>
                  </div>
                  
                  {expandedTrack === track.id && track.explanation && (
                    <div className="px-4 py-3 bg-gray-50">
                      <h5 className="text-sm font-medium mb-1">推薦理由:</h5>
                      <p className="text-sm text-gray-700">{track.explanation}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}