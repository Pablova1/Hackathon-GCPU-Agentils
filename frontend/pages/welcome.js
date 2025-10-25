import { useRouter } from 'next/router';
import CircularText from "../components/CircularText";
import styles from "../styles/Welcome.module.css";

export default function Welcome() {
  const router = useRouter();

  const handleSignIn = () => {
    router.push('/signin');
  };

  const handleLogIn = () => {
    router.push('/login');
  };

  return (
    <div className={styles.container}>
      {/* Bienvenue en haut */}
      <div className={styles.welcomeHeader}>
        <h1 className={styles.welcomeText}>Bienvenue</h1>
      </div>

      {/* MyPlate qui tourne au centre */}
      <div className={styles.centerSection}>
        <CircularText text="MY*PLATE*" spinDuration={15} onHover="speedUp" />
      </div>

      {/* Boutons en bas */}
      <div className={styles.buttonSection}>
        <button className={styles.authButton} onClick={handleSignIn}>
          Sign In
        </button>
        <button className={styles.authButton} onClick={handleLogIn}>
          Log In
        </button>
      </div>
    </div>
  );
}
