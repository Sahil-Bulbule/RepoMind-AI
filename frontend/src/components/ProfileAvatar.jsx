import React, { useState } from 'react';

export default function ProfileAvatar({ src, username, className = '' }) {
  const [imageFailed, setImageFailed] = useState(false);
  const initial = username?.trim().charAt(0).toUpperCase() || '?';

  return (
    <div className={`flex shrink-0 items-center justify-center overflow-hidden bg-slate-800 font-semibold text-white ${className}`}>
      {src && !imageFailed ? (
        <img
          src={src}
          alt={`${username || 'GitHub user'} avatar`}
          onError={() => setImageFailed(true)}
          className="h-full w-full object-cover"
        />
      ) : (
        initial
      )}
    </div>
  );
}