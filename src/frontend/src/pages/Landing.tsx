import React from 'react';
import { ArrowRight, CheckCircle2, Camera, MapPin, ShieldCheck, Users, Wrench } from 'lucide-react';
import { Link } from 'react-router-dom';

const featureCards = [
  { icon: Users, title: 'PUBLIC', text: 'Submit a category, location, and Before photo.', to: '/access/public' },
  { icon: Wrench, title: 'WORKERS', text: 'See issues automatically assigned to your service area and add After evidence.', to: '/access/worker' },
  { icon: ShieldCheck, title: 'MCC', text: 'Review every complaint and a live AI comparison score.', to: '/access/admin' },
];

const Landing: React.FC = () => (
  <main className="landing-shell overflow-hidden bg-[#030817] text-white">
    <div className="landing-grid" aria-hidden="true" />
    <div className="landing-glow landing-glow-one" aria-hidden="true" />
    <div className="landing-glow landing-glow-two" aria-hidden="true" />

    <nav className="relative z-10 mx-auto mt-5 flex max-w-6xl items-center justify-between rounded-2xl border border-blue-300/20 bg-slate-950/65 px-4 py-3 shadow-2xl shadow-blue-950/30 backdrop-blur-xl md:px-5">
      <Link to="/" className="flex items-center gap-3" aria-label="MysuruDrishti home">
        <span className="grid h-9 w-9 place-items-center rounded-xl border border-cyan-300/40 bg-cyan-300/10 text-sm font-black text-cyan-200">MD</span>
        <span><span className="block text-[10px] font-bold tracking-[0.18em] text-slate-400">MYSURU CITY CORPORATION</span><span className="text-base font-bold tracking-tight">Mysuru<span className="text-blue-400">Drishti</span></span></span>
      </Link>
      <div className="hidden items-center gap-6 text-sm text-slate-300 md:flex">
        <a href="#home" className="text-white">Home</a><a href="#login" className="hover:text-cyan-200">Login</a><a href="#about" className="hover:text-cyan-200">About</a><a href="#contact" className="hover:text-cyan-200">Contact</a>
      </div>
      <Link to="/access/public" className="inline-flex items-center gap-2 rounded-xl border border-cyan-300/30 bg-blue-500 px-3 py-2 text-sm font-semibold shadow-lg shadow-blue-500/25 transition hover:-translate-y-0.5 hover:bg-blue-400 md:px-4">Citizen Portal <ArrowRight className="h-4 w-4" /></Link>
    </nav>

    <section id="home" className="relative z-10 mx-auto grid max-w-6xl gap-12 px-6 pb-20 pt-16 lg:grid-cols-[1.03fr_.97fr] lg:items-center lg:pb-28 lg:pt-24">
      <div className="landing-enter">
        <p className="mb-5 inline-flex items-center gap-2 rounded-full border border-blue-300/20 bg-blue-400/10 px-3 py-1.5 text-xs font-bold tracking-[0.16em] text-cyan-100"><span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_10px_#00e5ff]" /> MYSURU CITY CORPORATION</p>
        <h1 className="max-w-xl text-5xl font-black leading-[0.98] tracking-tight sm:text-6xl lg:text-7xl">Report civic issues.<br />Track the work.<br />Verify the outcome with <span className="text-cyan-300 [text-shadow:0_0_28px_rgba(0,229,255,.5)]">AI.</span></h1>
        <p className="mt-6 max-w-xl text-base leading-7 text-slate-300 sm:text-lg">MysuruDrishti connects residents, field workers, and the MCC control room around transparent photo evidence.</p>
        <div id="login" className="mt-9 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          <Link to="/access/public" className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-500 px-5 py-3 font-bold shadow-lg shadow-blue-500/25 transition hover:-translate-y-1 hover:bg-blue-400"><Users className="h-4 w-4" /> Public login or sign up <ArrowRight className="h-4 w-4" /></Link>
          <Link to="/access/worker" className="inline-flex items-center justify-center gap-2 rounded-xl border border-blue-300/30 bg-white/5 px-5 py-3 font-semibold text-slate-100 transition hover:-translate-y-1 hover:border-cyan-300/70 hover:bg-blue-400/10"><Wrench className="h-4 w-4" /> Worker login</Link>
          <Link to="/access/admin" className="inline-flex items-center justify-center gap-2 rounded-xl border border-blue-300/30 bg-white/5 px-5 py-3 font-semibold text-slate-100 transition hover:-translate-y-1 hover:border-cyan-300/70 hover:bg-blue-400/10 sm:w-[386px]"><ShieldCheck className="h-4 w-4" /> Administrator</Link>
        </div>
      </div>

      <div className="landing-visual relative mx-auto w-full max-w-lg lg:justify-self-end" aria-label="MysuruDrishti report to verification workflow">
        <div className="landing-orbit" aria-hidden="true" />
        <div className="landing-city-card relative overflow-hidden rounded-3xl border border-cyan-200/30 bg-gradient-to-br from-[#132c58] via-[#0a1932] to-[#07101f] p-6 shadow-[0_0_55px_rgba(0,139,255,.25)]">
          <div className="absolute inset-0 opacity-25 [background-image:linear-gradient(rgba(0,229,255,.18)_1px,transparent_1px),linear-gradient(90deg,rgba(0,229,255,.18)_1px,transparent_1px)] [background-size:42px_42px]" />
          <div className="relative flex min-h-[330px] flex-col justify-between sm:min-h-[380px]">
            <div className="flex items-center justify-between"><span className="rounded-full border border-cyan-200/30 bg-slate-950/40 px-3 py-1 text-xs font-bold text-cyan-100">MYSURU LIVE GRID</span><MapPin className="h-5 w-5 text-cyan-300" /></div>
            <div className="mx-auto grid h-40 w-40 place-items-center rounded-full border border-cyan-200/30 bg-cyan-300/5 shadow-[inset_0_0_45px_rgba(0,229,255,.12)]"><div className="grid h-24 w-24 place-items-center rounded-full border border-blue-300/40 bg-blue-500/15"><span className="text-2xl font-black tracking-tighter text-cyan-100">MYS</span></div></div>
            <div className="grid grid-cols-3 gap-2 text-center text-[10px] font-bold tracking-wider text-slate-300"><span className="rounded-lg border border-white/10 bg-slate-950/40 px-2 py-2">REPORT</span><span className="rounded-lg border border-white/10 bg-slate-950/40 px-2 py-2">ASSIGN</span><span className="rounded-lg border border-cyan-200/30 bg-cyan-300/10 px-2 py-2 text-cyan-100">VERIFY</span></div>
          </div>
        </div>
        <div className="landing-float-card absolute -bottom-6 -left-3 rounded-2xl border border-cyan-200/30 bg-slate-950/85 p-3 shadow-xl backdrop-blur-xl sm:-left-10"><div className="flex gap-3"><span className="grid h-9 w-9 place-items-center rounded-xl bg-emerald-400/15 text-emerald-300"><CheckCircle2 className="h-5 w-5" /></span><div><p className="text-sm font-bold">Issue Resolved</p><p className="text-xs text-slate-400">Verified with photo evidence</p></div></div></div>
        <div className="landing-float-card absolute -right-2 top-16 rounded-2xl border border-blue-200/30 bg-slate-950/85 p-3 shadow-xl backdrop-blur-xl sm:-right-10"><div className="flex gap-3"><span className="grid h-9 w-9 place-items-center rounded-xl bg-blue-400/15 text-blue-200"><Camera className="h-5 w-5" /></span><div><p className="text-sm font-bold">Photo Evidence</p><p className="text-xs text-slate-400">Location · Time · Status</p></div></div></div>
      </div>
    </section>

    <section id="about" className="relative z-10 mx-auto max-w-6xl px-6 pb-20"><div className="grid gap-4 md:grid-cols-3">{featureCards.map(({ icon: Icon, title, text, to }) => <Link key={title} to={to} className="landing-feature group rounded-2xl border border-blue-200/15 bg-slate-900/55 p-6 backdrop-blur-sm"><div className="flex items-start justify-between"><span className="grid h-11 w-11 place-items-center rounded-xl border border-blue-300/25 bg-blue-400/10 text-cyan-200"><Icon className="h-5 w-5" /></span><ArrowRight className="h-5 w-5 text-slate-500 transition group-hover:translate-x-1 group-hover:text-cyan-200" /></div><h2 className="mt-7 font-bold tracking-[0.14em] text-cyan-100">{title}</h2><p className="mt-2 text-sm leading-6 text-slate-400">{text}</p></Link>)}</div></section>
    <footer id="contact" className="relative z-10 mx-auto flex max-w-6xl items-center gap-4 px-6 pb-10 text-center text-xs font-bold tracking-[0.18em] text-blue-300/70 before:h-px before:flex-1 before:bg-blue-300/20 after:h-px after:flex-1 after:bg-blue-300/20">CLEANER · SAFER · GREENER MYSURU</footer>
  </main>
);

export default Landing;
