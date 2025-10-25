import React, { useState } from 'react';
import Image from 'next/image';

export default function CircularText({ text = "MY*PLATE*", spinDuration = 10, onHover = "speedUp" }) {
  const [isHovered, setIsHovered] = useState(false);
  
  const chars = text.split('');
  const angleStep = 360 / chars.length;

  const animationDuration = isHovered && onHover === "speedUp" 
    ? spinDuration / 2 
    : spinDuration;

  return (
    <div 
      className="circular-text-wrapper"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Logo au centre */}
      <div className="logo-center">
        <Image 
          src="/Logo-2.png" 
          alt="MyPlate Logo" 
          width={160} 
          height={160}
          priority
        />
      </div>

      {/* Texte circulaire qui tourne */}
      <div className="circular-text-container">
        {chars.map((char, index) => (
          <span
            key={index}
            className="char"
            style={{
              transform: `rotate(${index * angleStep}deg)`,
            }}
          >
            {char}
          </span>
        ))}
      </div>
      
      <style jsx>{`
        .circular-text-wrapper {
          position: relative;
          width: 280px;
          height: 280px;
          margin: 0 auto;
        }

        .logo-center {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          z-index: 5;
        }

        .circular-text-container {
          position: absolute;
          top: 50%;
          left: 50%;
          width: 280px;
          height: 280px;
          transform: translate(-50%, -50%);
          animation: rotate ${animationDuration}s linear infinite;
          transition: animation-duration 0.5s ease;
        }

        .char {
          position: absolute;
          left: 50%;
          top: 0;
          transform-origin: 0 140px;
          font-size: 28px;
          font-weight: 900;
          color: #000;
          letter-spacing: 2px;
        }

        @keyframes rotate {
          from {
            transform: translate(-50%, -50%) rotate(0deg);
          }
          to {
            transform: translate(-50%, -50%) rotate(360deg);
          }
        }

        @media (max-width: 768px) {
          .circular-text-wrapper {
            width: 240px;
            height: 240px;
          }
          
          .circular-text-container {
            width: 240px;
            height: 240px;
          }

          .char {
            transform-origin: 0 120px;
            font-size: 24px;
          }
        }
      `}</style>
    </div>
  );
}
