// =============================================================================
// frontend/src/auth/cognitoAuth.js
// AWS Cognito Authentication Adapter (Template for future activation)
// =============================================================================

// Note: To wire AWS Cognito, developers usually install: npm install aws-amplify or use custom OAuth REST requests.
// This template is fully structure-compatible so you can easily drop in AWS Amplify's Auth class.

export const cognitoAuth = {
  /**
   * Listen to active Cognito session changes
   */
  onAuthStateChanged: (callback) => {
    console.info('[Cognito] Session listener initialized.');
    
    // Example Amplify wire-in:
    // import { Hub, Auth } from 'aws-amplify';
    // Auth.currentAuthenticatedUser()
    //   .then(user => callback(mapCognitoUser(user)))
    //   .catch(() => callback(null));
    // return Hub.listen('auth', ({ payload: { event, data } }) => {
    //   if (event === 'signIn') callback(mapCognitoUser(data));
    //   if (event === 'signOut') callback(null);
    // });
    
    // For now, return empty unsubscribe handler
    return () => {};
  },

  /**
   * AWS Cognito federated Google Sign-in redirection
   */
  loginWithGoogle: async () => {
    console.info('[Cognito] Google Federated login triggered.');
    // Example: await Auth.federatedSignIn({ provider: 'Google' });
    throw new Error("AWS Cognito Google Federated login is not configured yet. Set VITE_AUTH_PROVIDER=firebase for active runs.");
  },

  /**
   * Register standard email pools
   */
  signUpWithEmail: async (name, email, password) => {
    console.info('[Cognito] Pool Registration triggered: ', email);
    // Example:
    // const { user } = await Auth.signUp({
    //   username: email,
    //   password,
    //   attributes: { email, name }
    // });
    // return user;
    throw new Error("AWS Cognito Pool Sign-Up is not configured yet. Set VITE_AUTH_PROVIDER=firebase.");
  },

  /**
   * Sign in standard email pools
   */
  signInWithEmail: async (email, password) => {
    console.info('[Cognito] Pool Sign-In triggered: ', email);
    // Example:
    // const user = await Auth.signIn(email, password);
    // return mapCognitoUser(user);
    throw new Error("AWS Cognito Pool Sign-In is not configured yet. Set VITE_AUTH_PROVIDER=firebase.");
  },

  /**
   * Sign out current Cognito pool session
   */
  logout: async () => {
    console.info('[Cognito] Session sign-out triggered.');
    // Example: await Auth.signOut();
  },

  /**
   * Retrieve active AWS Cognito JWT access/id token string
   */
  getCurrentUserToken: async () => {
    console.info('[Cognito] Fetching active JWT session token.');
    // Example:
    // const session = await Auth.currentSession();
    // return session.getIdToken().getJwtToken();
    return "dummy-token-for-testing"; 
  }
};

/**
 * Utility mapper matching cognito attributes to unified user profile structure
 */
function mapCognitoUser(user) {
  return {
    uid: user.attributes?.sub || user.username,
    name: user.attributes?.name || user.username,
    email: user.attributes?.email,
    photoURL: user.attributes?.picture || null
  };
}
