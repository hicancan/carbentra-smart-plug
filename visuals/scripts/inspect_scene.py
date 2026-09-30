import bpy,json
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH':rows.append((o.name,len(o.data.vertices),len(o.data.polygons)))
print('SCENE_GEOMETRY',json.dumps(sorted(rows,key=lambda x:-x[2])[:20]));print('TOTAL',sum(r[1] for r in rows),sum(r[2] for r in rows))
