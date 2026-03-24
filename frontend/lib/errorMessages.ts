/**
 * Error Categorization & User-Friendly Messaging
 * Maps technical errors to user-friendly, actionable messages
 */

export interface FriendlyError {
  title: string;
  message: string;
  action: string;
  icon?: string;
}

export const errorCategoryMap: Record<string, FriendlyError> = {
  // Validation Errors
  'missing_field': {
    title: '❌ Missing Information',
    message: 'Please fill in all required fields and try again.',
    action: 'Review the form and make sure all required fields (marked with *) are completed.',
    icon: '⚠️',
  },
  'invalid_enum': {
    title: '❌ Invalid Selection',
    message: 'One of your selections is not valid. Please check dropdowns and try again.',
    action: 'Verify all dropdown selections are correct.',
    icon: '⚠️',
  },
  'invalid_range': {
    title: '❌ Invalid Value Range',
    message: 'A value is outside the acceptable range. For example, age must be 1-120 years, pain level 0-10.',
    action: 'Adjust values to be within valid ranges.',
    icon: '⚠️',
  },
  'symptom_empty': {
    title: '❌ No Symptoms Selected',
    message: 'Please select at least one symptom from the checklist.',
    action: 'Choose one or more clinical symptoms that the patient is experiencing.',
    icon: '⚠️',
  },
  'systemic_conditions_empty': {
    title: '❌ Medical History Required',
    message: 'Please indicate at least one systemic condition or select "None" if no conditions apply.',
    action: 'Update the "Systemic Conditions" section in Medical History.',
    icon: '⚠️',
  },

  // Server Errors
  'internal_server_error': {
    title: '⚠️ Server Error',
    message: 'The server encountered an issue processing your request. Our team has been notified.',
    action: 'Try again in a few moments. If the problem persists, contact support.',
    icon: '🔧',
  },
  'database_error': {
    title: '⚠️ Data Storage Issue',
    message: 'We could not save your data to the database. Please try again or contact support if the problem persists.',
    action: 'Retry your submission. If it continues to fail, contact the administrator.',
    icon: '💾',
  },
  'network_timeout': {
    title: '🌐 Connection Timeout',
    message: 'The request took too long to complete. Please check your internet connection and try again.',
    action: 'Verify your internet connectivity and retry your submission.',
    icon: '🌐',
  },
  'unauthorized': {
    title: '🔐 Session Expired',
    message: 'Your session has expired for security reasons. Please log in again.',
    action: 'Return to the login page and log in with your credentials.',
    icon: '🔒',
  },
  'forbidden': {
    title: '🚫 Access Denied',
    message: 'You do not have permission to perform this action.',
    action: 'Contact your administrator if you believe this is an error.',
    icon: '🔒',
  },
  'not_found': {
    title: '❌ Not Found',
    message: 'The requested resource could not be found.',
    action: 'Try reloading the page or returning to the dashboard.',
    icon: '🔍',
  },

  // Generic
  'unknown_error': {
    title: '❌ Something Went Wrong',
    message: 'An unexpected error occurred. Please try again or contact support if the problem persists.',
    action: 'Retry your submission or refresh the page.',
    icon: '❓',
  }
};

/**
 * Categorize an error based on its message and structure
 */
export function categorizeError(error: any): {
  category: string;
  details: any;
  rawError: any;
} {
  const message = typeof error === 'string'
    ? error
    : error?.message || String(error);

  const data = error?.response?.data || error?.data || {};
  const status = error?.response?.status || error?.status;

  // Check for specific HTTP status codes
  if (status === 422 || message.includes('422') || message.includes('validation')) {
    if (message.includes('systemic_conditions') || data.detail?.includes?.('systemic_conditions')) {
      return { category: 'systemic_conditions_empty', details: data, rawError: error };
    }
    if (message.includes('symptoms')) {
      return { category: 'symptom_empty', details: data, rawError: error };
    }
    return { category: 'missing_field', details: data, rawError: error };
  }

  if (status === 500 || message.includes('500') || message.includes('Internal server')) {
    return { category: 'internal_server_error', details: data, rawError: error };
  }

  if (status === 401 || message.includes('401') || message.includes('unauthorized') || message.includes('expired')) {
    return { category: 'unauthorized', details: data, rawError: error };
  }

  if (status === 403 || message.includes('403') || message.includes('forbidden')) {
    return { category: 'forbidden', details: data, rawError: error };
  }

  if (status === 404 || message.includes('404') || message.includes('not found')) {
    return { category: 'not_found', details: data, rawError: error };
  }

  if (message.includes('timeout') || message.includes('took too long') || message.includes('503')) {
    return { category: 'network_timeout', details: data, rawError: error };
  }

  if (message.includes('database') || message.includes('db')) {
    return { category: 'database_error', details: data, rawError: error };
  }

  return { category: 'unknown_error', details: data, rawError: error };
}

/**
 * Get a user-friendly error object from any error
 */
export function getUserFriendlyError(error: any): FriendlyError {
  const { category } = categorizeError(error);
  return errorCategoryMap[category] || errorCategoryMap['unknown_error'];
}

/**
 * Format error message for display
 */
export function formatErrorForDisplay(error: any): {
  title: string;
  message: string;
  action: string;
  icon: string;
  category: string;
} {
  const friendlyError = getUserFriendlyError(error);
  const { category } = categorizeError(error);

  return {
    ...friendlyError,
    icon: friendlyError.icon || '❌',
    category,
  };
}

/**
 * Get field-specific error messages (useful for form validation)
 */
export function getFieldError(fieldName: string, error: any): string | null {
  const data = error?.response?.data || error?.data || {};

  // Check if there are field-specific errors
  if (data.field_errors?.[fieldName]) {
    return data.field_errors[fieldName];
  }

  if (data.errors && Array.isArray(data.errors)) {
    const fieldError = data.errors.find((e: any) => e.field === fieldName);
    if (fieldError) {
      return fieldError.message;
    }
  }

  return null;
}
