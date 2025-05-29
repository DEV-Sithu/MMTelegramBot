require('dotenv').config();
const { Telegraf } = require('telegraf');

const bot = new Telegraf(process.env.BOT_TOKEN);

// မြန်မာပညာရေး၊ ကျန်းမာရေး၊ စီးပွားရေးနှင့် အားကစားဆိုင်ရာ မေးခွန်း ၁၀၀
const quizQuestions = [
  // ပညာရေး (25)
  {
    question: "မြန်မာနိုင်ငံ၏ ပထမဆုံး တက္ကသိုလ်မှာ မည်သည်နည်း။",
    options: ["ရန်ကုန်တက္ကသိုလ်", "မန္တလေးတက္ကသိုလ်", "ပုသိမ်တက္ကသိုလ်", "မော်လမြိုင်တက္ကသိုလ်"],
    correct: 0
  },
  {
    question: "အောက်ပါဘာသာရပ်များအနက် မြန်မာ့ရိုးရာ အတတ်ပညာမဟုတ်သောဘာသာရပ်မှာ မည်သည်နည်း။",
    options: ["ပန်းချီ", "ပန်းပု", "အင်ဂျင်နီယာ", "ကခြေသည်အတတ်"],
    correct: 2
  },
  {
    question: "မြန်မာနိုင်ငံ၏ ပညာရေးဝန်ကြီးဌာန လိုဂိုတွင် ပါဝင်သောအရာမှာ မည်သည်နည်း။",
    options: ["စာအုပ်", "ပေချပ်", "ကလောက်ဘုတ်", "ဘောပင်နှင့်မှန်"],
    correct: 3
  },
  {
    question: "ပထမဆုံး မြန်မာစာပေကျော်စွာ ဘွဲ့ရသူမှာ မည်သူနည်း။",
    options: ["ဆရာကြီးဦးဧမောင်", "ဆရာကြီးဦးဖိုးကျား", "ဆရာကြီးဦးဘလွင်", "ဆရာကြီးဦးသော်ဇင်"],
    correct: 0
  },
  {
    question: "အောက်ပါကျောင်းများအနက် မြန်မာနိုင်ငံ၏ အသက်အကြီးဆုံး အထက်တန်းကျောင်းမှာ မည်သည်နည်း။",
    options: ["ဗဟိုအမျိုးသားအထက်တန်းကျောင်း", "မြန်မာယူနီဗာစီတီ", "ဆိတ်ဖြူကုန်းအထက", "ဗဟိုအမျိုးသမီးအထက"],
    correct: 0
  },
  // ကျန်းမာရေး (25)
  {
    question: "အောက်ပါတို့အနက် မြန်မာ့ဆေးပညာတွင် အသုံးပြုသော သဘာဝဆေးဖက်ဝင်အပင်မှာ မည်သည်နည်း။",
    options: ["နနွင်း", "ပင်စိမ်း", "ကြက်သွန်ဖြူ", "အားလုံး"],
    correct: 3
  },
  {
    question: "ကမ္ဘာ့ကျန်းမာရေးအဖွဲ့၏ အတိုကောက်အမည်မှာ မည်သည်နည်း။",
    options: ["WHO", "UNICEF", "UNESCO", "FAO"],
    correct: 0
  },
  {
    question: "မြန်မာနိုင်ငံတွင် ပထမဆုံး ခွဲစိတ်ကုသမှုပြုလုပ်ခဲ့သော ဆေးရုံမှာ မည်သည်နည်း။",
    options: ["ရန်ကုန်အထွေထွေရုံး", "မန္တလေးအထွေထွေရုံး", "ဆေးတက္ကသိုလ် (၁) ရုံး", "ပြည်သူ့ဆေးရုံ"],
    correct: 0
  },
  {
    question: "အောက်ပါအစားအစာများအနက် ဗီတာမင် C အများဆုံးပါဝင်သော အသီးမှာ မည်သည်နည်း။",
    options: ["သံပုရာသီး", "ကမ္ဘာ့သရက်သီး", "စတော်ဘယ်ရီ", "အမဲသား"],
    correct: 0
  },
  {
    question: "သွေးတိုးရောဂါကို ထိန်းချုပ်ရန်အတွက် အကောင်းဆုံးနည်းလမ်းမှာ မည်သည်နည်း။",
    options: ["အငန်လျှော့စားခြင်း", "အားကစားလုပ်ခြင်း", "စိတ်ဖိစီးမှုလျှော့ချခြင်း", "အားလုံး"],
    correct: 3
  },
  // စီးပွားရေး (25)
  {
    question: "မြန်မာနိုင်ငံ၏ အဓိကတင်ပို့ကုန်မှာ မည်သည်နည်း။",
    options: ["ဆန်", "သစ်", "ဓာတ်ငွေ့", "ပဲမျိုးစုံ"],
    correct: 2
  },
  {
    question: "မြန်မာနိုင်ငံတွင် ပထမဆုံးသော စတော့အိတ်ချိန်းကို မည်သည့်နှစ်တွင် စတင်ဖွင့်လှစ်ခဲ့သနည်း။",
    options: ["1996", "2000", "2015", "2020"],
    correct: 0
  },
  {
    question: "အောက်ပါဘဏ်များအနက် မြန်မာနိုင်ငံ၏ ပထမဆုံး နိုင်ငံပိုင်ဘဏ်မှာ မည်သည်နည်း။",
    options: ["KBZ ဘဏ်", "ရန်ကုန်ဘဏ်", "ဂျီအိုင်စီဘဏ်", "CB ဘဏ်"],
    correct: 1
  },
  {
    question: "မြန်မာနိုင်ငံ၏ အကြီးဆုံး စက်မှုဇုန်မှာ မည်သည့်နေရာတွင်တည်ရှိသနည်း။",
    options: ["သန်လျင်", "သီလဝါ", "ပြည်ကြီးတံခွန်", "ပုသိမ်"],
    correct: 0
  },
  {
    question: "မြန်မာနိုင်ငံတွင် နှစ်စဉ်ကျင်းပသော နိုင်ငံတကာကုန်စည်ပြပွဲကို မည်သည့်မြို့တွင်ကျင်းပသနည်း။",
    options: ["ရန်ကုန်", "မန္တလေး", "နေပြည်တော်", "ပဲခူး"],
    correct: 0
  },
  // အားကစား (25)
  {
    question: "မြန်မာ့ရိုးရာ အားကစားနည်းမှာ မည်သည်နည်း။",
    options: ["ဘောလုံး", "ကြက်တောက်ကွက်", "ကြက်လျှာကွက်", "ပိုက်ကျော်ခြင်း"],
    correct: 1
  },
  {
    question: "အောက်ပါအားကစားသမားများအနက် နိုင်ငံတကာဆုရရှိခဲ့သူမှာ မည်သူနည်း။",
    options: ["ဦးကျော်စိုး", "ဦးစိုးဝင်း", "ဦးအောင်ကြီး", "ဦးသိန်းထွန်း"],
    correct: 0
  },
  {
    question: "မြန်မာနိုင်ငံ၏ အမျိုးသားအားကစားနေ့မှာ မည်သည့်နေ့ဖြစ်သနည်း။",
    options: ["ဒီဇင်ဘာ ၁", "နိုဝင်ဘာ ၁၈", "ဒီဇင်ဘာ ၁၉", "နိုဝင်ဘာ ၂၇"],
    correct: 2
  },
  {
    question: "အောက်ပါအားကစားနည်းများအနက် အိုလံပစ်တွင် ပါဝင်သောနည်းမှာ မည်သည်နည်း။",
    options: ["ကြက်တောက်ကွက်", "ပိုက်ကျော်ခြင်း", "မြန်မာ့ဂျူဒို", "တိုက်ကွမ်ဒို"],
    correct: 3
  },
  {
    question: "မြန်မာနိုင်ငံ၏ အမျိုးသားဘောလုံးအသင်းကို မည်သည့်အမည်ဖြင့်ခေါ်သနည်း။",
    options: ["ခြင်္သေ့ငယ်", "ခြင်္သေ့များ", "ကျားများ", "ကြက်ဖများ"],
    correct: 0
  },
  // ... ဒီနေရာမှာ မေးခွန်း  ထပ်ဖြည့်ပါ ...
];

// User state များ သိမ်းဆည်းရန်
const userState = new Map();

// UI အတွက် helper functions
function createProgressBar(current, total, width = 10) {
  const progress = Math.round((current / total) * width);
  return `[${'▓'.repeat(progress)}${'░'.repeat(width - progress)}]`;
}

function getRandomEmoji() {
  const emojis = ["✨", "🌟", "💫", "🔥", "🚀", "🎯", "🧠", "💡"];
  return emojis[Math.floor(Math.random() * emojis.length)];
}

bot.start((ctx) => {
  const userId = ctx.from.id;
  userState.set(userId, {
    currentQuestion: 0,
    score: 0
  });
  
  ctx.replyWithMarkdown(
    `🌟 *မြန်မာပညာရေး၊ ကျန်းမာရေး၊ စီးပွားရေးနှင့် အားကစား Quiz Bot မှ ကြိုဆိုပါတယ်* 🌟\n\n` +
    `ဤဘော့သည် မြန်မာ့ဗဟုသုတများကို စမ်းသပ်ပေးမည့် အထူးပြုလုပ်ထားသော Quiz ဘော့ဖြစ်ပါသည်။\n\n` +
    `အောက်ပါ command များကို သုံးပါ:\n` +
    `🚀 /quiz - Quiz စတင်ရန်\n` +
    `📊 /score - ရမှတ်ကြည့်ရန်\n` +
    `ℹ️ /help - အကူအညီ`,
    {
      reply_markup: {
        inline_keyboard: [
          [{ text: "🚀 ဂိမ်းစတင်မယ်", callback_data: "start_quiz" }],
          [{ text: "📊 ရမှတ်ကြည့်မယ်", callback_data: "show_score" }]
        ]
      }
    }
  );
});

bot.action('start_quiz', (ctx) => {
  const userId = ctx.from.id;
  const state = userState.get(userId) || { currentQuestion: 0, score: 0 };
  state.currentQuestion = 0;
  state.score = 0;
  userState.set(userId, state);
  
  ctx.replyWithMarkdown(
    `🎮 *ဂိမ်းစတင်ပါပြီ!* ${getRandomEmoji()}\n\n` +
    `မေးခွန်း ${quizQuestions.length} ခု ဖြေဆိုရမည်။\n` +
    `အောက်ပါခလုတ်ကိုနှိပ်ပြီး စတင်နိုင်ပါတယ်!`,
    {
      reply_markup: {
        inline_keyboard: [
          [{ text: "✅ စတင်မယ်", callback_data: "next_question" }]
        ]
      }
    }
  );
});

bot.action('next_question', (ctx) => {
  const userId = ctx.from.id;
  sendQuestion(ctx, userId);
});

function sendQuestion(ctx, userId) {
  const state = userState.get(userId);
  if (state.currentQuestion >= quizQuestions.length) {
    showResults(ctx, userId);
    return;
  }
  
  const question = quizQuestions[state.currentQuestion];
  const progressBar = createProgressBar(state.currentQuestion, quizQuestions.length);
  
  const keyboard = {
    inline_keyboard: [
      ...question.options.map((option, index) => [
        { 
          text: `${['A', 'B', 'C', 'D'][index]}. ${option}`, 
          callback_data: `ans_${index}`
        }
      ]),
      [{ text: "⏩ ကျော်မယ်", callback_data: "skip_question" }]
    ]
  };
  
  ctx.replyWithMarkdown(
    `📝 *မေးခွန်း ${state.currentQuestion + 1}/${quizQuestions.length}*\n\n` +
    `${progressBar}\n\n` +
    `❓ ${question.question}`,
    { reply_markup: keyboard }
  );
}

bot.action('skip_question', (ctx) => {
  const userId = ctx.from.id;
  const state = userState.get(userId);
  state.currentQuestion++;
  userState.set(userId, state);
  
  ctx.replyWithMarkdown(
    `⏭️ *မေးခွန်းကို ကျော်လိုက်ပါပြီ!*\n\n` +
    `နောက်မေးခွန်းဆီသို့ ဆက်သွားပါမည်...`
  );
  
  setTimeout(() => sendQuestion(ctx, userId), 1500);
});

bot.action(/ans_(\d+)/, (ctx) => {
  const userId = ctx.from.id;
  const state = userState.get(userId);
  const selectedOption = parseInt(ctx.match[1]);
  const currentQuestion = quizQuestions[state.currentQuestion];
  
  let replyText = '';
  
  if (selectedOption === currentQuestion.correct) {
    state.score++;
    replyText = `🎉 *မှန်ပါတယ်!* ${getRandomEmoji()}\n\n` +
                `သင်ရွေးချယ်ထားတာ: ${currentQuestion.options[selectedOption]}\n` +
                `+1 မှတ် ရရှိပါပြီ!`;
  } else {
    replyText = `❌ *မှားပါတယ်!*\n\n` +
                `သင်ရွေးချယ်ထားတာ: ${currentQuestion.options[selectedOption]}\n` +
                `မှန်တဲ့အဖြေက: *${currentQuestion.options[currentQuestion.correct]}*`;
  }
  
  ctx.replyWithMarkdown(replyText);
  
  // နောက်မေးခွန်းဆီသို့
  state.currentQuestion++;
  userState.set(userId, state);
  
  setTimeout(() => {
    if (state.currentQuestion < quizQuestions.length) {
      sendQuestion(ctx, userId);
    } else {
      showResults(ctx, userId);
    }
  }, 2500);
});

function showResults(ctx, userId) {
  const state = userState.get(userId);
  const total = quizQuestions.length;
  const percentage = Math.round((state.score / total) * 100);
  
  let resultEmoji = "";
  if (percentage >= 80) resultEmoji = "🏆";
  else if (percentage >= 60) resultEmoji = "🎯";
  else if (percentage >= 40) resultEmoji = "🙂";
  else resultEmoji = "😢";
  
  ctx.replyWithMarkdown(
    `🏁 *ဂိမ်းပြီးဆုံးပါပြီ!* ${resultEmoji}\n\n` +
    `✅ မှန်သောအဖြေများ: ${state.score}/${total}\n` +
    `📊 ရာခိုင်နှုန်း: ${percentage}%\n\n` +
    `ထပ်မံကစားလိုပါက /start ကိုနှိပ်ပါ။`,
    {
      reply_markup: {
        inline_keyboard: [
          [{ text: "🔄 ပြန်စမယ်", callback_data: "start_quiz" }],
          [{ text: "📊 ရမှတ်ကြည့်မယ်", callback_data: "show_score" }]
        ]
      }
    }
  );
}

bot.action('show_score', (ctx) => {
  const userId = ctx.from.id;
  const state = userState.get(userId);
  
  if (state && state.currentQuestion > 0) {
    const total = quizQuestions.length;
    const percentage = Math.round((state.score / total) * 100);
    
    ctx.replyWithMarkdown(
      `📊 *လက်ရှိရမှတ်များ*\n\n` +
      `✅ မှန်သောအဖြေများ: *${state.score}/${total}*\n` +
      `📈 ရာခိုင်နှုန်း: *${percentage}%*`
    );
  } else {
    ctx.replyWithMarkdown(
      `ℹ️ သင်ဂိမ်းမစသေးပါ။\n` +
      `ဂိမ်းစတင်ရန် /start ကိုနှိပ်ပါ။`
    );
  }
});

bot.help((ctx) => {
  ctx.replyWithMarkdown(
    `ℹ️ *အကူအညီ*\n\n` +
    `*Commands:*\n` +
    `/start - Bot စတင်ရန်\n` +
    `/quiz - Quiz ဂိမ်းစတင်ရန်\n` +
    `/score - လက်ရှိရမှတ်ကြည့်ရနု\n` +
    `/help - အကူအညီ\n\n` +
    `*ဂိမ်းကစားနည်း:*\n` +
    `1. /quiz ဖြင့်ဂိမ်းစတင်ပါ\n` +
    `2. ပေးထားသောရွေးချယ်စရာများမှဖြေဆိုပါ\n` +
    `3. ရမှတ်များကိုကြည့်ရှုနိုင်ပါတယ်`
  );
});

bot.command('quiz', (ctx) => {
  const userId = ctx.from.id;
  const state = userState.get(userId) || { currentQuestion: 0, score: 0 };
  state.currentQuestion = 0;
  state.score = 0;
  userState.set(userId, state);
  sendQuestion(ctx, userId);
});

bot.launch();
console.log('Bot is running...');

// Graceful shutdown
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
