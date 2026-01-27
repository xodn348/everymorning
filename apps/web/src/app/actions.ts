'use server'

import { createClient } from '@supabase/supabase-js'

export async function subscribe(formData: FormData) {
  const email = formData.get('email') as string
  const fields = formData.getAll('fields') as string[]
  
  if (!email || !email.includes('@')) {
    return { error: 'Please enter a valid email address' }
  }
  
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!
  )
  
  const { error } = await supabase
    .from('subscribers')
    .insert({ 
      email, 
      preferred_fields: fields.length > 0 ? fields : null 
    })
  
  if (error) {
    if (error.code === '23505') {
      return { error: 'Already subscribed!' }
    }
    console.error('Subscription error:', error)
    return { error: 'Something went wrong' }
  }
  
  return { success: true }
}
