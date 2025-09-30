// Login.js
import { useForm } from 'react-hook-form';
import styles from './Auth.module.css';
import { useNavigate } from 'react-router-dom';


const Login = ({ onLogin }) => {
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    mode: 'onBlur',
    reValidateMode: 'onBlur',
  });

  const onSubmit = (data) => {
    if (data.username === 'admin' && data.password === 'admin123') {
      onLogin();
      navigate('/dashboard');
      return;
    }
    alert('Invalid credentials. Try admin/admin123.');
  };

  return (
    <div className={styles.authContainer}>
      <div className={styles.road}></div>
      <form className={styles.authForm} onSubmit={handleSubmit(onSubmit)}>
        <div className={styles.trafficSignalHeader}>
          <div className={styles.trafficSignal}>
            <div className={styles.signalRed}></div>
            <div className={styles.signalYellow}></div>
            <div className={styles.signalGreen}></div>
          </div>
          <h2 className={styles.authTitle}>Smart Traffic Management</h2>
        </div>
        <div className={styles.inputGroup}>
          <label htmlFor="username" className={styles.label}>Username</label>
          <input id="username" type="text" className={styles.input} {...register('username', { required: 'Username is required' })} />
          {errors.username && <div className={styles.error}>{errors.username.message}</div>}
        </div>
        <div className={styles.inputGroup}>
          <label htmlFor="password" className={styles.label}>Password</label>
          <input id="password" type="password" className={styles.input} {...register('password', { required: 'Password is required' })} />
          {errors.password && <div className={styles.error}>{errors.password.message}</div>}
        </div>
        <button type="submit" className={styles.submitButton}>Login</button>
      </form>
    </div>
  );
};

export default Login;
