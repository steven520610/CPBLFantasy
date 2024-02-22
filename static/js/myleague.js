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


const matchup = Vue.createApp({
    data() {
        return {
            matchup_list: matchup_list
        }
    },
    delimiters: ['[[', ']]']
})
app.mount("#app");
matchup.mount("#matchupContainer");