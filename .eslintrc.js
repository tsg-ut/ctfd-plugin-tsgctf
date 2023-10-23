module.exports = {
  'env': {
    'browser': true,
    'commonjs': true,
    'es2021': true,
    'jquery': true,
  },
  'extends': [
    'google',
    'prettier',
  ],
  'plugins': [
    'jquery',
  ],
  'overrides': [
    {
      'env': {
        'node': true,
      },
      'files': [
        '.eslintrc.{js,cjs}',
      ],
      'parserOptions': {
        'sourceType': 'script',
      },
    },
  ],
  'parserOptions': {
    'ecmaVersion': 'latest',
  },
  'rules': {
  },
};
