import { useForm } from 'react-hook-form';
import styles from './Auth.module.css';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useState, useRef, useEffect } from 'react';

const Login = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const loginButtonRef = useRef(null);
  
  // Realistic live stats with slow updates
  const [liveStats, setLiveStats] = useState({
    vehicles: 1247,
    signals: 42,
    efficiency: 98
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    mode: 'onBlur',
    reValidateMode: 'onBlur',
  });

  // Realistic live counter updates (slow changes every 20-45 seconds)
  useEffect(() => {
    const updateStats = () => {
      setLiveStats(prev => ({
        vehicles: prev.vehicles + Math.floor(Math.random() * 5) - 2, // -2 to +2
        signals: prev.signals + (Math.random() > 0.9 ? (Math.random() > 0.5 ? 1 : -1) : 0), // Rare changes
        efficiency: Math.max(94, Math.min(99, prev.efficiency + (Math.random() > 0.5 ? 0.1 : -0.1)))
      }));
    };

    // Update every 25-40 seconds for realistic feel
    const interval = setInterval(updateStats, 25000 + Math.random() * 15000);
    return () => clearInterval(interval);
  }, []);

  const onSubmit = async (data) => {
    setIsLoading(true);
    setError('');
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';
      const response = await axios.post(`${apiUrl}/auth/login`, data, {
        withCredentials: true,
      });

      if (response.status === 200) {
        const { accessToken } = response.data;
        if (loginButtonRef.current) {
          loginButtonRef.current.style.background =
            'linear-gradient(45deg, #00ff88, #00cc66)';
        }
        if (accessToken) {
          localStorage.setItem('accessToken', accessToken);
          setTimeout(() => navigate('/userDetails'), 1000);
        }
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Authentication failed. Please try again.');
      // subtle error color flash
      if (loginButtonRef.current) {
        loginButtonRef.current.style.background = 'linear-gradient(45deg, #ff4444, #cc0000)';
        setTimeout(() => {
          if (loginButtonRef.current) {
            loginButtonRef.current.style.background = 'linear-gradient(45deg, #22c55e, #16a34a)';
          }
        }, 1800);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.authContainer}>
      {/* LIVE TRAFFIC MONITORING (keep) */}
      <div className={styles.digitalDisplay}>
        <div className={styles.displayText}>
          <span className={styles.liveIndicator}>🔴 LIVE</span>
          TRAFFIC MONITORING ACTIVE
        </div>
        <div className={styles.stats}>
          <span>🚗 {liveStats.vehicles.toLocaleString()} Vehicles</span>
          <span>🚦 {liveStats.signals} Signals</span>
          <span>📊 {liveStats.efficiency.toFixed(1)}% Efficiency</span>
        </div>
      </div>

      {/* LOGIN FORM (signal light kept) */}
      <form className={styles.authForm} onSubmit={handleSubmit(onSubmit)}>
        <div className={styles.formHeader}>
          <div className={styles.trafficSignal}>
            <div className={styles.signalContainer}>
              <div className={`${styles.light} ${styles.red}`}></div>
              <div className={`${styles.light} ${styles.yellow}`}></div>
              <div className={`${styles.light} ${styles.green}`}></div>
            </div>
          </div>

          <div className={styles.titleSection}>
            <h1 className={styles.mainTitle}>TRAFFIC AI</h1>
            <div className={styles.subtitle}>Smart Management System</div>
            <div className={styles.govBadge}>Government of Odisha</div>
          </div>
        </div>

        {error && <div className={styles.errorDisplay}>{error}</div>}

        <div className={styles.formBody}>
          <div className={styles.inputContainer}>
            <label className={styles.inputLabel}>
              <span className={styles.labelIcon}>👤</span>
              Username
            </label>
            <input
              type="text"
              className={styles.formInput}
              placeholder="Enter username"
              {...register('username', {
                required: 'Username is required',
                minLength: { value: 3, message: 'Must be at least 3 characters' }
              })}
              disabled={isLoading}
            />
            {errors.username && <div className={styles.fieldError}>{errors.username.message}</div>}
          </div>

          <div className={styles.inputContainer}>
            <label className={styles.inputLabel}>
              <span className={styles.labelIcon}>🔒</span>
              Password
            </label>
            <input
              type="password"
              className={styles.formInput}
              placeholder="Enter password"
              {...register('password', {
                required: 'Password is required',
                minLength: { value: 6, message: 'Must be at least 6 characters' }
              })}
              disabled={isLoading}
            />
            {errors.password && <div className={styles.fieldError}>{errors.password.message}</div>}
          </div>

          <button
            ref={loginButtonRef}
            type="submit"
            className={styles.submitBtn}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className={styles.btnIcon}>⏳</span>
                Authenticating...
              </>
            ) : (
              <>
                <span className={styles.btnIcon}>🚀</span>
                Access System
              </>
            )}
          </button>
        </div>

        <div className={styles.formFooter}>
          <div className={styles.securityNote}>🔒 Secure Authentication Portal</div>
          <div className={styles.projectInfo}>SIH25050 • Transportation & Logistics</div>
        </div>
      </form>

      {/* ROAD + MOVING TRUCK (with dashed white centerline) */}
      <div className={styles.road}>
        <div className={styles.truck}>🚚</div>
        <div className={styles.ambulance}>🚑</div>
        <div className={styles.police}>🚓</div>
        <div className={styles.fire}>🚒</div>
      </div>
    </div>
  );
};

export default Login;