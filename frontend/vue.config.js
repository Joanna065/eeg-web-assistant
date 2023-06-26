module.exports = {
    transpileDependencies: ['vuetify'],
    chainWebpack: config => {
        // Plotly loader
        config.module
            .rule('plotly')
            .test(/\.js$/)
            .use('ify-loader')
            .loader('ify-loader')
            .end()
            .use('transform-loader?plotly.js/tasks/compress_attributes.js')
            .loader('transform-loader?plotly.js/tasks/compress_attributes.js')
            .end();
    }
};
