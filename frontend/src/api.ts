export async function request<T>(path:string, body?:unknown):Promise<T>{
 const response=await fetch(path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});
 if(!response.ok) throw new Error(`Service unavailable (${response.status})`);
 return response.json();
}
