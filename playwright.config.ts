import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Autohire testing framework
 * Comprehensive E2E and automation testing setup
 */
export default defineConfig({
  // Test directory configuration
  testDir: './tests/automation',
  
  // Global test configuration
  timeout: 30 * 1000, // 30 seconds per test
  expect: {
    timeout: 10 * 1000, // 10 seconds for assertions
  },
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry configuration
  retries: process.env.CI ? 2 : 1,
  
  // Parallel test execution
  workers: process.env.CI ? 2 : undefined,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'tests/automation/playwright-report' }],
    ['junit', { outputFile: 'tests/automation/test-results/results.xml' }],
    ['json', { outputFile: 'tests/automation/test-results/results.json' }],
    ['line'],
    ...(process.env.CI ? [['github']] : [])
  ],
  
  // Global test setup and teardown
  globalSetup: require.resolve('./tests/automation/global-setup.ts'),
  globalTeardown: require.resolve('./tests/automation/global-teardown.ts'),
  
  // Test output directory
  outputDir: 'tests/automation/test-results/',
  
  // Screenshots and videos
  use: {
    // Browser context options
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    // Trace collection
    trace: 'on-first-retry',
    
    // Screenshot configuration
    screenshot: 'only-on-failure',
    
    // Video recording
    video: 'retain-on-failure',
    
    // Action timeout
    actionTimeout: 10 * 1000,
    
    // Navigation timeout
    navigationTimeout: 30 * 1000,
    
    // Locale and timezone
    locale: 'en-AU',
    timezoneId: 'Australia/Melbourne',
    
    // Geolocation for location-based testing
    geolocation: { longitude: 144.9631, latitude: -37.8136 }, // Melbourne
    permissions: ['geolocation'],
    
    // Color scheme
    colorScheme: 'light',
    
    // User agent
    userAgent: 'AutohireTestBot/1.0 (Playwright)',
    
    // HTTP credentials for basic auth if needed
    // httpCredentials: { username: 'test', password: 'test' },
    
    // Ignore HTTPS errors in test environments
    ignoreHTTPSErrors: true,
    
    // Browser launch options
    launchOptions: {
      slowMo: process.env.SLOW_MO ? parseInt(process.env.SLOW_MO) : 0,
    }
  },

  // Test projects for different browsers and configurations
  projects: [
    // Setup project for authentication and data seeding
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    
    // Desktop browsers
    {
      name: 'chromium-desktop',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }
      },
      dependencies: ['setup'],
    },
    
    {
      name: 'firefox-desktop',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: { width: 1920, height: 1080 }
      },
      dependencies: ['setup'],
    },
    
    {
      name: 'webkit-desktop',
      use: { 
        ...devices['Desktop Safari'],
        viewport: { width: 1920, height: 1080 }
      },
      dependencies: ['setup'],
    },
    
    // Mobile browsers
    {
      name: 'mobile-chrome',
      use: { 
        ...devices['Pixel 5']
      },
      dependencies: ['setup'],
    },
    
    {
      name: 'mobile-safari',
      use: { 
        ...devices['iPhone 12']
      },
      dependencies: ['setup'],
    },
    
    // Tablet browsers
    {
      name: 'tablet-chrome',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 768, height: 1024 }
      },
      dependencies: ['setup'],
    },
    
    // Accessibility testing
    {
      name: 'accessibility',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }
      },
      testMatch: /.*\.accessibility\.spec\.ts/,
      dependencies: ['setup'],
    },
    
    // Performance testing
    {
      name: 'performance',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }
      },
      testMatch: /.*\.performance\.spec\.ts/,
      dependencies: ['setup'],
    },
    
    // Security testing
    {
      name: 'security',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }
      },
      testMatch: /.*\.security\.spec\.ts/,
      dependencies: ['setup'],
    },
    
    // API testing
    {
      name: 'api',
      use: {
        baseURL: process.env.API_BASE_URL || 'http://localhost:8000/api',
      },
      testMatch: /.*\.api\.spec\.ts/,
      dependencies: ['setup'],
    },
    
    // Visual regression testing
    {
      name: 'visual-regression',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }
      },
      testMatch: /.*\.visual\.spec\.ts/,
      dependencies: ['setup'],
    },
    
    // Cross-browser compatibility
    {
      name: 'edge',
      use: { 
        ...devices['Desktop Edge'],
        channel: 'msedge'
      },
      dependencies: ['setup'],
    }
  ],

  // Web server configuration for local development
  webServer: process.env.CI ? undefined : [
    {
      command: 'cd backend && python functional_server.py',
      port: 8000,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000, // 2 minutes
      env: {
        NODE_ENV: 'test',
        DATABASE_URL: 'postgresql://postgres:postgres@localhost:5432/autohire_test',
        TESTING: 'true'
      }
    },
    {
      command: 'cd frontend && npm run dev',
      port: 3000,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000, // 2 minutes
    }
  ],

  // Test patterns
  testMatch: [
    '**/*.spec.ts',
    '**/*.test.ts'
  ],
  
  // Files to ignore
  testIgnore: [
    '**/node_modules/**',
    '**/dist/**',
    '**/build/**',
    '**/.git/**'
  ],

  // Metadata collection
  metadata: {
    'test-framework': 'Playwright',
    'project': 'Autohire',
    'environment': process.env.NODE_ENV || 'test',
    'version': process.env.VERSION || '1.0.0'
  },

  // Test configuration overrides
  ...(process.env.CI && {
    // CI-specific configuration
    workers: 2,
    retries: 3,
    reporter: [
      ['html', { outputFolder: 'playwright-report' }],
      ['junit', { outputFile: 'test-results.xml' }],
      ['github']
    ],
    use: {
      trace: 'retain-on-failure',
      video: 'retain-on-failure',
      screenshot: 'only-on-failure'
    }
  }),

  // Experimental features
  // experimentalCTComponent: './tests/component-tests',
  
  // Global test hooks
  // globalSetup: require.resolve('./global-setup'),
  // globalTeardown: require.resolve('./global-teardown'),
});