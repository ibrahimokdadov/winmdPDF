import type { Config } from 'jest'

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['<rootDir>/electron/__tests__/**/*.test.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/renderer/$1',
  },
  transform: {
    '^.+\\.ts$': ['ts-jest', { tsconfig: 'electron/tsconfig.json' }],
  },
}

export default config
