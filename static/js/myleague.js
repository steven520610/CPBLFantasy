const app = Vue.createApp({
    data() {
        return {
            showText: false,
            currentTime: ''
        };
    },
    methods: {
        updateTime() {
            this.currentTime = new Date();
            this.showText = true;
        },
        clearTime() {
            this.showText = false;
        }
    },
    delimiters: ['[[', ']]']
})
app.mount("#app");