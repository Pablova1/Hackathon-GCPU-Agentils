import { useRouter } from 'next/router';
import Image from 'next/image';
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

      {/* Logo au centre */}
      <div className={styles.centerSection}>
        <Image 
          src="/Logo-2.png" 
          alt="MyPlate Logo" 
          width={200} 
          height={200}
          priority
          style={{ objectFit: 'contain' }}
        />
      </div>

      {/* MY*PLATE* qui tourne en bas */}
      <div className={styles.rotatingTextSection}>
        <CircularText text="MY*PLATE*" spinDuration={15} onHover="speedUp" />
      </div>

      {/* Boutons en bas */}
      <div className={styles.buttonSection}>
        <button className={styles.authButton} onClick={handleSignIn}>
          S'inscrire
        </button>
        <button className={styles.authButton} onClick={handleLogIn}>
          Se connecter
        </button>
      </div>
    </div>
  );
}
