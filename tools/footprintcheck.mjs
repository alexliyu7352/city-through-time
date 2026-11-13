// Appearance sidecar contract: node tools/footprintcheck.mjs --selftest | <city folder>
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { cityGeometry, todayFootprintFingerprint, buildTodayFootprints } from '../engine/studio.js';

if (process.argv[2] === '--selftest') {
  const M = { scale:.001, box:[0,0,1,1], b:[[1985,12]], p:[[0,.012,[[[0,0],[.02,0],[.02,.02],[0,.02]]],0]], bex:1 };
  const before = JSON.stringify(M), white = cityGeometry(M), bytes = Buffer.from(white.attributes.position.array.buffer).toString('hex');
  assert.equal(await todayFootprintFingerprint(M),'2e4e17dbc807c2b99526e5fc1adf301242da6ab7f88572c5be6a0ddecb38cc58');
  assert.deepEqual((await buildTodayFootprints(M,{enabled:false})).skipBi,[]);
  const child = (x,h) => ({ rings:[[[x,.001],[x+.008,.001],[x+.008,.019],[x,.019]]],h:h*.001,base:0,height_m:h });
  const sidecar = { version:1, enabled:true, model_fingerprint:await todayFootprintFingerprint(M), replacements:[{pi:0,bi:0,children:[child(.001,12),child(.011,30)]}] };
  const out = await buildTodayFootprints(M,sidecar,{early:new Map([[0,1987]]),renew:new Map([[0,[.4,2015,2020]]]),grow:new Map([[0,7]])});
  assert.deepEqual(out.skipBi,[0]);assert.deepEqual(out.skipCentres,[[.01,.01]]);
  for (let i=0;i<out.geometry.attributes.position.count;i++) {
    const A=out.geometry.attributes;assert.equal(A.aBi.getX(i),0);assert.equal(A.aData.getX(i),1987);
    assert.ok(Math.abs(A.aCtr.getX(i)-.01)<1e-8 && Math.abs(A.aCtr.getY(i)-.01)<1e-8);
    assert.equal(A.aGrowT.getX(i),7);assert.ok(Math.abs(A.aGrowH.getX(i)-.4)<1e-7);
  }
  assert.equal(JSON.stringify(M),before);assert.equal(Buffer.from(white.attributes.position.array.buffer).toString('hex'),bytes);
  const changed=structuredClone(M);changed.b[0][0]=2000;
  await assert.rejects(buildTodayFootprints(changed,sidecar),/another prepared model/);
  await assert.rejects(buildTodayFootprints(M,{...sidecar,replacements:[...sidecar.replacements,...sidecar.replacements]}),/duplicate/);
  white.dispose();out.geometry.dispose();console.log('footprintcheck selftest: fingerprint, disabled, split identity/time/centre, immutable white geometry, stale and duplicate refusal OK');
} else {
  const city=process.argv[2];if(!city)throw new Error('usage: footprintcheck.mjs --selftest | <city folder>');
  const M=JSON.parse(fs.readFileSync(`${city}/build/data/model.json`)),S=JSON.parse(fs.readFileSync(`${city}/build/data/today_footprints.json`));
  const before=JSON.stringify(M),out=await buildTodayFootprints(M,S);
  if (out.geometry) {
    const A=out.geometry.attributes, centres=new Map(out.skipBi.map((bi,i)=>[bi,out.skipCentres[i]]));
    for(let i=0;i<A.position.count;i++) {
      const bi=A.aBi.getX(i),c=centres.get(bi);assert.ok(c);assert.equal(A.aData.getX(i),Math.fround(M.b[bi][0]));
      assert.equal(A.aCtr.getX(i),Math.fround(c[0]));assert.equal(A.aCtr.getY(i),Math.fround(c[1]));
    }
    console.log(`footprintcheck: ${out.skipBi.length} parents; ${A.position.count} sparse vertices; every child inherits the original year and centre`);
    out.geometry.dispose();
  } else assert.deepEqual(out.skipBi,[]);
  assert.equal(JSON.stringify(M),before);console.log('footprintcheck: prepared model unchanged');
}
