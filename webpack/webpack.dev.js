const { merge } = require('webpack-merge');

const common = require('./webpack.common.js');

module.exports = merge(common, {
    mode: 'development',
    devServer: {
        static: './dist',
        host: '0.0.0.0',
        port: 3000,
        hot: true,
        devMiddleware: {
            writeToDisk: true,
        }
    },
});
