import './styles.css';

const app = document.getElementById('app');

if (!app) {
  throw new Error('Missing #app root element');
}

app.innerHTML = `
  <main class="shell">
    <section class="card">
      <h1>AITeam TypeScript App</h1>
      <p>Pipeline 已切换到组件化 TypeScript 工程模式，等待生成具体业务代码。</p>
    </section>
  </main>
`;
