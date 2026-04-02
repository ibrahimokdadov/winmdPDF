import type { Config } from 'jest'

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['<rootDir>/electron/__tests__/**/*.test.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/renderer/$1',
    '^electron$': '<rootDir>/electron/__mocks__/electron.ts',
    '^../renderer/lib/markdown-to-html$': '<rootDir>/electron/__mocks__/markdown-to-html.ts',
  },
  transform: {
    '^.+\\.ts$': ['ts-jest', { tsconfig: 'electron/tsconfig.json' }],
  },
}

export default config
