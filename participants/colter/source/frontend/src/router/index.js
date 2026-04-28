import { createRouter, createWebHistory } from 'vue-router';

const HomeView = () => import('../views/HomeView.vue');
const PresentationEditor = () => import('../views/PresentationEditor.vue');
const TemplateEditor = () => import('../views/TemplateEditor.vue');

const routes = [
  { path: '/', component: HomeView, name: 'home' },
  {
    path: '/presentations/:id',
    component: PresentationEditor,
    name: 'presentation',
    props: true,
  },
  {
    path: '/templates/:id',
    component: TemplateEditor,
    name: 'template',
    props: true,
  },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
