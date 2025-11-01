import { motion, useMotionValue, useTransform } from 'framer-motion';
import { useState } from 'react';
import styles from '../styles/MealCardStack.module.css';

function MealCard({ children, onSendToBack, sensitivity }) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useTransform(y, [-100, 100], [30, -30]);
  const rotateY = useTransform(x, [-100, 100], [-30, 30]);

  function handleDragEnd(_, info) {
    if (Math.abs(info.offset.x) > sensitivity || Math.abs(info.offset.y) > sensitivity) {
      onSendToBack();
    } else {
      x.set(0);
      y.set(0);
    }
  }

  return (
    <motion.div
      className={styles.cardRotate}
      style={{ x, y, rotateX, rotateY }}
      drag
      dragConstraints={{ top: 0, right: 0, bottom: 0, left: 0 }}
      dragElastic={0.6}
      whileTap={{ cursor: 'grabbing' }}
      onDragEnd={handleDragEnd}
    >
      {children}
    </motion.div>
  );
}

export default function MealCardStack({ suggestions }) {
  const [cards, setCards] = useState(
    suggestions.slice(0, 5).map((suggestion, index) => ({
      id: index,
      ...suggestion
    }))
  );

  const sendToBack = (id) => {
    setCards(prev => {
      const newCards = [...prev];
      const index = newCards.findIndex(card => card.id === id);
      const [card] = newCards.splice(index, 1);
      newCards.unshift(card);
      return newCards;
    });
  };

  if (cards.length === 0) {
    return null;
  }

  return (
    <div className={styles.stackContainer}>
      {cards.map((card, index) => {
        const randomRotate = Math.random() * 6 - 3;

        return (
          <MealCard key={card.id} onSendToBack={() => sendToBack(card.id)} sensitivity={150}>
            <motion.div
              className={styles.card}
              animate={{
                rotateZ: (cards.length - index - 1) * 3 + randomRotate,
                scale: 1 + index * 0.04 - cards.length * 0.04,
                transformOrigin: '50% 90%'
              }}
              initial={false}
              transition={{
                type: 'spring',
                stiffness: 260,
                damping: 20
              }}
            >
              <div className={styles.cardContent}>
                <div className={styles.mealHeader}>
                  <h3 className={styles.mealName}>{card.name}</h3>
                  {card.meal_time && (
                    <span className={styles.mealTime}>{card.meal_time}</span>
                  )}
                </div>
                <p className={styles.mealDescription}>{card.description}</p>
                {card.calories && (
                  <div className={styles.mealCalories}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FF9800" strokeWidth="2">
                      <path d="M12 2v20M2 12h20"/>
                    </svg>
                    <span>{card.calories} kcal</span>
                  </div>
                )}
              </div>
            </motion.div>
          </MealCard>
        );
      })}
    </div>
  );
}
