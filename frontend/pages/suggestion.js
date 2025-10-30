import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../hooks/useAuth';
import { apiClient } from '../utils/api';
import NavigationFooter from '../components/NavigationFooter';
import styles from '../styles/Suggestion.module.css';

export default function Suggestion() {
  const router = useRouter();
  const { isAuthenticated, isLoading, userId, firstName, lastName, logout } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [motivationMessage, setMotivationMessage] = useState('');
  const [mealSuggestions, setMealSuggestions] = useState([]);
  const [suggestionStatus, setSuggestionStatus] = useState('');
  const [generatedAt, setGeneratedAt] = useState(null);
  const [profileComplete, setProfileComplete] = useState(true);

  // Check authentication on load
  useEffect(() => {
    if (isLoading) return;
    
    if (!isAuthenticated || !userId) {
      router.push('/welcome');
    } else {
      // Load suggestions from DB
      fetchSuggestionsFromDB(userId);
    }
  }, [router, isAuthenticated, isLoading, userId]);

  const handleLogout = () => {
    logout();
  };

  const fetchSuggestionsFromDB = async (user_id) => {
    setLoading(true);
    setError(null);
    
    try {
      // Vérifier d'abord si le profil est complet
      const profileData = await apiClient.get(`/api/profile/check?user_id=${user_id}`);
      
      console.log('Profile data:', profileData); // Debug
      
      // Vérifier principalement avec profile_completed
      const isProfileComplete = profileData.profile_completed === true;
      
      if (!isProfileComplete) {
        console.log('Profile incomplete. profile_completed:', profileData.profile_completed); // Debug
        setProfileComplete(false);
        setLoading(false);
        return;
      }
      
      console.log('Profile is complete!'); // Debug
      
      // Get motivation
      const motivationData = await apiClient.get(`/api/suggestions/motivation/${user_id}`);
      
      // Get meals
      const mealsData = await apiClient.get(`/api/suggestions/meals/${user_id}`);
      
      // Update state
      setMotivationMessage(motivationData.motivation_message || '');
      setMealSuggestions(mealsData.meal_suggestions || []);
      setSuggestionStatus(motivationData.status || mealsData.status || '');
      setGeneratedAt(motivationData.generated_at || mealsData.generated_at);
      setError(null);
      
    } catch (err) {
      setError(err.message);
      setMotivationMessage('');
      setMealSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    if (userId) {
      fetchSuggestionsFromDB(userId);
    }
  };

  const handleGenerateSuggestions = async () => {
    if (!userId) return;
    
    setLoading(true);
    setSuggestionStatus('generating');
    
    try {
      await apiClient.post(`/api/suggestions/trigger/${userId}`, {});
      
      // Wait a few seconds then refresh
      setTimeout(() => {
        fetchSuggestionsFromDB(userId);
      }, 3000);
      
    } catch (err) {
      console.error('Error:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const handleGoBack = () => {
    router.push('/');
  };

  if (!isAuthenticated || !userId) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!profileComplete) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <button className={styles.backButton} onClick={handleGoBack}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
          <h1 className={styles.title}>My Suggestions</h1>
          <div className={styles.placeholder}></div>
        </div>

        <main className={styles.main}>
          <div className={styles.warningCard}>
            <div className={styles.warningIcon}>⚠️</div>
            <h2>Incomplete Profile</h2>
            <p className={styles.warningText}>
              To receive personalized suggestions, you need to complete your profile first!
            </p>
            <p className={styles.warningSubtext}>
              We need to know your age, weight, height and goals to suggest meals adapted to your needs.
            </p>
            <div className={styles.buttonGroup}>
              <button className={styles.primaryButton} onClick={() => router.push('/onboarding-new')}>
                Complete my profile
              </button>
              <button className={styles.secondaryButton} onClick={handleGoBack}>
                Back
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading suggestions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Error</h2>
          <p>{error}</p>
          <button className={styles.primaryButton} onClick={handleRefresh}>
            Try again
          </button>
        </div>
      </div>
    );
  }

  // Render content based on status
  const renderContent = () => {
    if (suggestionStatus === 'generating') {
      return (
        <div className={styles.statusCard}>
          <div className={styles.spinner}></div>
          <h2>⏳ Generating...</h2>
          <p>Your personalized suggestions are being created. This may take a few moments.</p>
          <button className={styles.secondaryButton} onClick={handleRefresh}>
            🔄 Refresh
          </button>
        </div>
      );
    }

    if (suggestionStatus === 'failed') {
      return (
        <div className={styles.errorCard}>
          <h2>❌ Generation Error</h2>
          <p>An error occurred while generating suggestions.</p>
          <p className={styles.errorSubtext}>
            Make sure you have completed your profile and scanned at least one meal.
          </p>
          <div className={styles.buttonGroup}>
            <button className={styles.primaryButton} onClick={handleGenerateSuggestions}>
              🔄 Try again
            </button>
            <button className={styles.secondaryButton} onClick={() => router.push('/onboarding-new')}>
              Complete my profile
            </button>
            <button className={styles.secondaryButton} onClick={handleGoBack}>
              Back
            </button>
          </div>
        </div>
      );
    }

    if (!motivationMessage && mealSuggestions.length === 0 && suggestionStatus !== 'failed') {
      return (
        <div className={styles.emptyCard}>
          <h2>✨ Generate your personalized suggestions</h2>
          <p>
            We're ready to analyze your profile and eating habits to offer you personalized suggestions!
          </p>
          <div className={styles.buttonGroup}>
            <button className={styles.primaryButton} onClick={handleGenerateSuggestions}>
              ✨ Generate my suggestions
            </button>
            <button className={styles.secondaryButton} onClick={handleGoBack}>
              Back
            </button>
          </div>
        </div>
      );
    }

    return (
      <>
        {/* Motivation message */}
        {motivationMessage && (
          <div className={styles.motivationCard}>
            <h2>💪 Your daily motivation</h2>
            <p className={styles.motivationText}>{motivationMessage}</p>
            {generatedAt && (
              <p className={styles.generatedDate}>
                Generated on {new Date(generatedAt).toLocaleDateString('en-US', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            )}
          </div>
        )}

        {/* Refresh button */}
        <div className={styles.refreshContainer}>
          <button className={styles.refreshButton} onClick={handleRefresh}>
            🔄 Refresh
          </button>
        </div>

        {/* Meal suggestions */}
        {mealSuggestions.length > 0 && (
          <div className={styles.suggestionsSection}>
            <h2 className={styles.sectionTitle}>🍽️ Your meal suggestions</h2>
            <div className={styles.mealsGrid}>
              {mealSuggestions.map((meal, index) => (
                <div key={index} className={styles.mealCard}>
                  <div className={styles.mealHeader}>
                    <h3>{meal.meal_name || `Meal ${index + 1}`}</h3>
                    {meal.meal_type && (
                      <span className={styles.mealType}>{meal.meal_type}</span>
                    )}
                  </div>

                  {meal.description && (
                    <p className={styles.mealDescription}>{meal.description}</p>
                  )}

                  {meal.macros && (
                    <div className={styles.macrosContainer}>
                      <div className={styles.macroItem}>
                        <div className={styles.macroLabel}>Calories</div>
                        <div className={`${styles.macroValue} ${styles.calories}`}>
                          {meal.macros.calories || 0} kcal
                        </div>
                      </div>
                      <div className={styles.macroItem}>
                        <div className={styles.macroLabel}>Protein</div>
                        <div className={`${styles.macroValue} ${styles.protein}`}>
                          {meal.macros.proteins || 0}g
                        </div>
                      </div>
                      <div className={styles.macroItem}>
                        <div className={styles.macroLabel}>Carbs</div>
                        <div className={`${styles.macroValue} ${styles.carbs}`}>
                          {meal.macros.carbs || 0}g
                        </div>
                      </div>
                      <div className={styles.macroItem}>
                        <div className={styles.macroLabel}>Fats</div>
                        <div className={`${styles.macroValue} ${styles.fats}`}>
                          {meal.macros.fats || 0}g
                        </div>
                      </div>
                    </div>
                  )}

                  {meal.ingredients && meal.ingredients.length > 0 && (
                    <div className={styles.ingredientsContainer}>
                      <h4>Ingredients:</h4>
                      <ul>
                        {meal.ingredients.map((ingredient, idx) => (
                          <li key={idx}>{ingredient}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {meal.preparation_tips && (
                    <div className={styles.tipsContainer}>
                      <h4>💡 Preparation tips</h4>
                      <p>{meal.preparation_tips}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </>
    );
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <button className={styles.backButton} onClick={handleGoBack}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>My Personalized Suggestions</h1>
          <p className={styles.subtitle}>Based on your eating history</p>
        </div>
        <button className={styles.logoutButton} onClick={handleLogout} title="Logout">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
      </div>

      {/* Main content */}
      <main className={styles.main}>
        {renderContent()}
      </main>

      {/* Footer avec navigation */}
      <NavigationFooter />
    </div>
  );
}














