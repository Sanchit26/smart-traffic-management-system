import { useForm } from 'react-hook-form';
import styles from './Auth.module.css';
import { Link } from 'react-router-dom';
 import axios from 'axios';

const Register = () => {
  const {
  register,
  handleSubmit,
  formState: { errors },
} = useForm({
  mode: 'onChange',          // Validate on first change
  reValidateMode: 'onChange', // Revalidate on every change
});




const onSubmit = async (data) => {
  try {
    console.log('Registration form submitted', data);

    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';
    const response = await axios.post(`${apiUrl}/auth/register`, data);

    if (response.status === 201) {
      alert('Registration successful!');
      // Optional: reset form or redirect to login
    }
  } catch (error) {
    console.error('Registration error:', error);

    if (error.response) {
      // Server responded with a non-2xx status
      alert(error.response.data.message || 'Registration failed');
    } else {
      // Unexpected error (like network failure)
      alert('An unexpected error occurred. Please try again.');
    }
  }
};


  return (
    <div className={styles.authContainer}>
      <form className={styles.authForm} onSubmit={handleSubmit(onSubmit)}>
        <h2 className={styles.authTitle}>Create an account</h2>

        <div className={styles.inputGroup}>
          <label htmlFor="name" className={styles.label}>Full Name</label>
          <input
            id="name"
            type="text"
            className={styles.input}
            {...register('name', {
              required: 'Name is required',
              minLength: {
                value: 3,
                message: 'Name must be at least 3 characters',
              },
            })}
          />
          {errors.name && <div className={styles.error}>{errors.name.message}</div>}
        </div>

        <div className={styles.inputGroup}>
          <label htmlFor="email" className={styles.label}>Email</label>
          <input
            id="email"
            type="email"
            className={styles.input}
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: 'Invalid email address',
              },
            })}
          />
          {errors.email && <div className={styles.error}>{errors.email.message}</div>}
        </div>

        <div className={styles.inputGroup}>
          <label htmlFor="mobile" className={styles.label}>Mobile Number</label>
          <input
            id="mobile"
            type="text"
            className={styles.input}
            {...register('mobile', {
              required: 'Mobile number is required',
              pattern: {
                value: /^[0-9]{10}$/,
                message: 'Mobile number must be 10 digits',
              },
            })}
          />
          {errors.mobile && <div className={styles.error}>{errors.mobile.message}</div>}
        </div>

        <div className={styles.inputGroup}>
          <label htmlFor="password" className={styles.label}>Password</label>
          <input
            id="password"
            type="password"
            className={styles.input}
            {...register('password', {
              required: 'Password is required',
              minLength: {
                value: 6,
                message: 'Password must be at least 6 characters',
              },
            })}
          />
          {errors.password && <div className={styles.error}>{errors.password.message}</div>}
        </div>

        <button type="submit" className={styles.submitButton}>
          Register
        </button>

        <p className={styles.toggleText}>
          Already have an account?{' '}
          <Link to="/login" className={styles.toggleLink}>Login</Link>
        </p>
      </form>
    </div>
  );
};

export default Register;
