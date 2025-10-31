import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../hooks/useAuth';
import { apiClient } from '../utils/api';
import NavigationFooter from '../components/NavigationFooter';
import MealCardStack from '../components/MealCardStack';
import styles from '../styles/Home.module.css';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading, userId, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [mealSuggestions, setMealSuggestions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (isLoading) return;

      if (!isAuthenticated || !userId) {
        router.push('/welcome');
        return;
      }

      try {
        // Charger les stats ET les suggestions en parallèle
        const [statsData, suggestionsData] = await Promise.all([
          apiClient.get(`/meals/user/${userId}/home-stats`),
          apiClient.get(`/api/suggestions/meals/${userId}`)
        ]);

        console.log('Stats data:', statsData);
        console.log('Suggestions data:', suggestionsData);

        setStats(statsData);
        // Correction : lire la clé last_suggestion.meal_suggestions si elle existe
        if (suggestionsData.last_suggestion && suggestionsData.last_suggestion.meal_suggestions) {
          setMealSuggestions({ meal_suggestions: suggestionsData.last_suggestion.meal_suggestions });
        } else if (suggestionsData.meal_suggestions) {
          setMealSuggestions({ meal_suggestions: suggestionsData.meal_suggestions });
        } else {
          setMealSuggestions({ meal_suggestions: [] });
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router, isAuthenticated, isLoading, userId]);

  const handleBackClick = () => {
    router.push('/');
  };

  const handleProfileClick = () => {
    // Rediriger vers la page d'onboarding pour modifier les réponses
    router.push('/onboarding-new');
  };

  const handleLogout = () => {
    logout();
  };

  // Get current week days
  const getWeekDays = () => {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const today = new Date();
    const currentDay = today.getDay();
    const weekDays = [];

    for (let i = 0; i < 7; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() - currentDay + i);
      weekDays.push({
        name: days[i],
        date: date.getDate(),
        hasActivity: false // will be updated with backend data
      });
    }

    return weekDays;
  };

  // Check if a day has scanned meals
  const checkActivityForDay = (dayDate, calendar) => {
    if (!calendar || !calendar.days_with_meals) return false;
    return calendar.days_with_meals.includes(dayDate);
  };

  const weekDays = stats ? getWeekDays().map(day => ({
    ...day,
    hasActivity: checkActivityForDay(day.date, stats.current_month_calendar)
  })) : getWeekDays();

  // Get score color
  const getScoreColor = (score) => {
    if (score >= 4.5) return '#4CAF50'; // Green
    if (score >= 3.5) return '#8BC34A'; // Light green
    if (score >= 2.5) return '#FFC107'; // Orange
    if (score >= 1.5) return '#FF9800'; // Dark orange
    return '#F44336'; // Red
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Chargement...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <p>❌ {error}</p>
          <button onClick={() => router.reload()}>Réessayer</button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <button className={styles.profileIcon} onClick={handleProfileClick} title="Edit my profile">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#666" strokeWidth="2">
            <circle cx="12" cy="8" r="4"/>
            <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>
          </svg>
        </button>
        <h1 className={styles.title}>My profils</h1>
        <button className={styles.logoutButton} onClick={handleLogout} title="Logout">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
      </header>

      <main className={styles.main}>
        {/* Meal Suggestions Section */}
        {mealSuggestions && (
          <div className={styles.suggestionsSection}>
            <h2 className={styles.sectionTitle}>🍽️ Meal Suggestions for You</h2>
            
            {mealSuggestions.meal_suggestions && mealSuggestions.meal_suggestions.length > 0 ? (
              <>
                <MealCardStack suggestions={mealSuggestions.meal_suggestions} />
                {mealSuggestions.meal_suggestions.length > 5 && (
                  <button 
                    className={styles.viewAllButton}
                    onClick={() => router.push('/suggestion')}
                  >
                    View All Suggestions ({mealSuggestions.meal_suggestions.length})
                  </button>
                )}
              </>
            ) : (
              <div className={styles.noSuggestions}>
                <p>📸 Scan your first meal to get personalized suggestions!</p>
                <button 
                  className={styles.scanButton}
                  onClick={() => router.push('/')}
                >
                  Scan a Meal
                </button>
              </div>
            )}
          </div>
        )}

        {/* Total scanned meals */}
        <div className={styles.statCard}>
          <div className={styles.statIcon}>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#66BB6A" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div className={styles.statContent}>
            <h2 className={styles.statTitle}>Scanned Meals</h2>
            <p className={styles.statValue}>{stats?.total_meals_scanned || 0}</p>
            <p className={styles.statSubtext}>since the beginning</p>
          </div>
        </div>

        {/* Week calendar */}
        <div className={styles.calendarCard}>
          <h2 className={styles.cardTitle}>This Week</h2>
          <div className={styles.weekCalendar}>
            {weekDays.map((day, index) => (
              <div key={index} className={styles.dayColumn}>
                <div className={styles.dayName}>{day.name}</div>
                <div className={`${styles.dayCircle} ${day.hasActivity ? styles.active : ''}`}>
                  {day.hasActivity && (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  )}
                </div>
              </div>
            ))}
          </div>
          <p className={styles.calendarSubtext}>
            {weekDays.filter(d => d.hasActivity).length} day{weekDays.filter(d => d.hasActivity).length !== 1 ? 's' : ''} with scanned meals
          </p>
        </div>

        {/* Weekly score */}
        {stats?.weekly_score && (
          <div className={styles.scoreCard}>
            <h2 className={styles.cardTitle}>Weekly Score</h2>
            <div className={styles.scoreContent}>
              <div 
                className={styles.scoreCircle}
                style={{ borderColor: getScoreColor(stats.weekly_score.score) }}
              >
                <span 
                  className={styles.scoreValue}
                  style={{ color: getScoreColor(stats.weekly_score.score) }}
                >
                  {stats.weekly_score.score.toFixed(1)}
                </span>
                <span className={styles.scoreMax}>/5</span>
              </div>
              <div className={styles.scoreComment}>
                <p>{stats.weekly_score.comment}</p>
              </div>
            </div>
          </div>
        )}

        {/* Additional information */}
        <div className={styles.infoCard}>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Current Month</span>
            <span className={styles.infoValue}>
              {stats?.current_month_calendar?.total_meals_in_month || 0} meals
            </span>
          </div>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Active Days This Month</span>
            <span className={styles.infoValue}>
              {stats?.current_month_calendar?.days_with_meals?.length || 0} days
            </span>
          </div>
        </div>
      </main>

      {/* Footer avec navigation */}
      <NavigationFooter />
    </div>
  );
}
