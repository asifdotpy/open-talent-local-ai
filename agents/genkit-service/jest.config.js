module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: [
    "**/src/tests/**/*.test.ts"
  ],
  moduleFileExtensions: [
    "ts",
    "js",
    "json",
    "node"
  ],
  transform: {
    "^.+\\.ts$": [
      "ts-jest",
      {
        tsconfig: 'tsconfig.json'
      }
    ]
  },
  silent: true
};
